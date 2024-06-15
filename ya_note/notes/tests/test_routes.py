from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

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

    def test_pages_availability(self):
        """Доступ для неаунтефицированного пользователя."""
        urls = (
            self.URL_NOTES_HOME,
            self.URL_USERS_LOGIN,
            self.URL_USERS_LOGOUT,
            self.URL_USERS_SIGNUP,
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Доступ для аунтефицированных пользователей."""
        urls = (
            self.URL_NOTES_LIST,
            self.URL_NOTES_ADD,
            self.URL_NOTES_SUCCESS,
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.reader_logged.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):

        users_statuses = (
            (self.author_logged, HTTPStatus.OK),
            (self.reader_logged, HTTPStatus.NOT_FOUND),
        )

        for client, status in users_statuses:

            for url in (
                self.URL_NOTES_EDIT,
                self.URL_NOTES_DELETE,
                self.URL_NOTES_DETAIL,
            ):
                with self.subTest(name=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            self.URL_NOTES_EDIT,
            self.URL_NOTES_DELETE,
            self.URL_NOTES_DETAIL,
            self.URL_NOTES_LIST,
            self.URL_NOTES_ADD,
            self.URL_NOTES_SUCCESS,
        )
        for url in urls:
            with self.subTest(name=url):
                redirect_url = f'{self.URL_USERS_LOGIN}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
