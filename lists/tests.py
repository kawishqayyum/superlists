from django.test import TestCase
from lists.models import Item, List


class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'lists/home.html')


class ListAndItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text = 'First (ever) item'
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = 'Item, the second'
        second_item.list = list_
        second_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()
        self.assertEqual(len(saved_items), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]

        self.assertEqual(first_saved_item.text, 'First (ever) item')
        self.assertEqual(first_item.list, list_)

        self.assertEqual(second_saved_item.text, 'Item, the second')
        self.assertEqual(second_item.list, list_)


class ListViewTests(TestCase):
    def test_uses_lists_template(self):
        response = self.client.get('/lists/the-only-list-in-the-world/')
        self.assertTemplateUsed(response, 'lists/list.html')

    def test_display_all_items(self):
        list_ = List.objects.create()
        Item.objects.create(text='itemey 1', list=list_)
        Item.objects.create(text='itemey 2', list=list_)

        response = self.client.get('/lists/the-only-list-in-the-world/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')


class NewListTests(TestCase):
    def test_can_save_a_post_request(self):
        self.client.post('/lists/new', data={'item_text': 'A new list'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list')

    def test_redirect_after_post(self):
        response = self.client.post(
            '/lists/new',
            data={'item_text': 'A new list'}
        )

        self.assertRedirects(response, '/lists/the-only-list-in-the-world/')
