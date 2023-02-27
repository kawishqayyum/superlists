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
        self.assertEqual(
            response['location'],
            'lists/the-only-list-in-the-world/'
        )

    def test_only_save_items_when_necessary(self):
        self.client.get('/')
        self.assertEqual(Item.objects.count(), 0)


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


class ListViewTests(TestCase):
    def test_uses_lists_template(self):
        response = self.client.get('/lists/the-only-list-in-the-world/')
        self.assertTemplateUsed(response, 'lists/list.html')

    def test_display_all_items(self):
        Item.objects.create(text='itemey 1')
        Item.objects.create(text='itemey 2')

        response = self.client.get('/lists/the-only-list-in-the-world/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
