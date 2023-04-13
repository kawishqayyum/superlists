import os
import random
from invoke import Responder
from fabric import task, Config
from patchwork.files import exists, append


REPO_URL = 'https://github.com/kawishqayyum/superlists'
sudo_pass = os.environ.get('FAB_PASS')
config = Config(overrides={'sudo': {'password': sudo_pass}})



@task
def deploy(c):
    site_folder = f'/home/{c.user}/sites/{c.host}'
    source_folder = site_folder + '/source'

    _create_directory_structure_if_necessary(c, site_folder)
    _get_latest_source(c, source_folder)
    _update_settings(c, source_folder)
    _update_venv(c, source_folder)
    _update_static_files(c, source_folder)
    _update_database(c, source_folder)
    _setup_nginx(c, source_folder)
    _setup_gunicorn(c, source_folder)


@task
def _create_directory_structure_if_necessary(c, site_folder):
    for subfolder in ('.env', 'database', 'source', 'static'):
        c.run(f'mkdir -p {site_folder}/{subfolder}')


@task
def _get_latest_source(c, source_folder):
    if exists(c, source_folder + '/.git'):
        c.run(f'cd {source_folder} && git fetch')
    else:
        c.run(f'git clone {REPO_URL} {source_folder}')

    current_commit = c.local('git log -n 1 --format=%H').stdout
    c.run(f'cd {source_folder} && git reset --hard {current_commit}')


@task
def _update_settings(c, source_folder):
    settings_path = source_folder + '/superlists/settings.py'
    c.run(f'sed -i \'s/DEBUG = True/DEBUG = False/\' {settings_path}')
    c.run(f'sed -i \'s/ALLOWED_HOSTS = .*$/ALLOWED_HOSTS = ["{c.host}"]/\' {settings_path}')

    secret_key_file = source_folder + '/superlists/secret_key.py'

    if not exists(c, secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(c, secret_key_file, f'SECRET_KEY = "{key}"')

    append(c, settings_path, '\n\nfrom .secret_key import SECRET_KEY')


@task
def _update_venv(c, source_folder):
    venv_folder = source_folder + '/../.env'

    if not exists(c, venv_folder + '/bin/pip'):
        c.run(f'python3 -m venv {venv_folder}')

    c.run(f'{venv_folder}/bin/pip install -r {source_folder}/requirements.txt')


@task
def _update_static_files(c, source_folder):
    collect_static = '../.env/bin/python3 manage.py collectstatic --noinput'
    c.run(f'cd {source_folder} && {collect_static}')


@task
def _update_database(c, source_folder):
    migrate_db = '../.env/bin/python3 manage.py migrate --noinput'
    c.run(f'cd {source_folder} && {migrate_db}')


@task
def _setup_nginx(c, source_folder):
    c.config = config

    nginx_conf_template = source_folder + '/deploy_tools/nginx.template.conf'
    sites_available = f'/etc/nginx/sites-available/{c.host}'
    sites_enabled = f'/etc/nginx/sites-enabled/{c.host}'

    if not exists(c, sites_available):
        c.sudo(
            f'sed \'s/SITENAME/{c.host}/\' {nginx_conf_template} | sudo tee {sites_available}'
        )

    if not exists(c, sites_enabled):
        c.sudo(f'sudo ln -s {sites_available} {sites_enabled}')

    c.sudo('sudo systemctl daemon-reload')
    c.sudo('sudo systemctl reload nginx')


@task
def _setup_gunicorn(c, source_folder):
    c.config = config
    gunicorn_conf = source_folder + '/deploy_tools/gunicorn-systemd.template.service'
    gunicorn_service = f'/etc/systemd/system/gunicorn-{c.host}.service'

    if not exists(c, gunicorn_service):
        print(5*'*#*#*#', 'I wasn\'t here right?')
        c.sudo(
            f'sed \'s/SITENAME/{c.host}/\' {gunicorn_conf} | sudo tee {gunicorn_service}'
        )

    c.sudo(f'sudo systemctl enable gunicorn-{c.host}')
    c.sudo(f'sudo systemctl start gunicorn-{c.host}')
