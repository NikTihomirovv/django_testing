from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class Fixtures(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='test_author')
        cls.reader = User.objects.create(username='test_reader')
        cls.author_logged = Client()
        cls.reader_logged = Client()
        cls.author_logged.force_login(cls.author)
        cls.reader_logged.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='test_header',
            text='test_text',
            slug='test_note',
            author=cls.author
        )

        cls.form_data = {
            'title': 'test_form_title',
            'text': 'test_form_text',
            'slug': 'test_form_slug',
        }

        cls.URL_USERS_LOGIN = reverse('users:login')
        cls.URL_USERS_LOGOUT = reverse('users:logout')
        cls.URL_USERS_SIGNUP = reverse('users:signup')

        cls.URL_NOTES_HOME = reverse('notes:home')
        cls.URL_NOTES_LIST = reverse('notes:list')
        cls.URL_NOTES_ADD = reverse('notes:add')
        cls.URL_NOTES_SUCCESS = reverse('notes:success')

        cls.URL_NOTES_DETAIL = reverse('notes:detail', args=(cls.note.slug,))
        cls.URL_NOTES_EDIT = reverse('notes:edit', args=(cls.note.slug,))
        cls.URL_NOTES_DELETE = reverse('notes:delete', args=(cls.note.slug,))
