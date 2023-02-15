from django.test import TestCase
from lists.models import Item


class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'lists/home.html')

    def test_can_save_a_post_request(self):
        self.client.post('/', data={'item_text': 'A new list'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list')

    def test_redirect_after_post(self):
        response = self.client.post('/', data={'item_text': 'A new list'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_only_save_items_when_necessary(self):
        self.client.get('/')
        self.assertEqual(Item.objects.count(), 0)

    def test_display_all_list_items(self):
        Item.objects.create(text='first item')
        Item.objects.create(text='second item')

        response = self.client.get('/')

        self.assertIn('first item', response.content.decode('utf8'))
        self.assertIn('second item', response.content.decode('utf8'))


class ItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        first_item = Item()
        first_item.text = 'First (ever) item'
        first_item.save()

        second_item = Item()
        second_item.text = 'Item, the second'
        second_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(len(saved_items), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]

        self.assertEqual(first_saved_item.text, 'First (ever) item')
        self.assertEqual(second_saved_item.text, 'Item, the second')
