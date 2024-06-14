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

    def test_pages_availability(self):
        """Доступ для неаунтефицированного пользователя."""
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Доступ для аунтефицированных пользователей."""
        urls = (
            ('notes:list'),
            ('notes:add'),
            ('notes:success'),
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.reader_logged.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):

        users_statuses = (
            (self.author_logged, HTTPStatus.OK),
            (self.reader_logged, HTTPStatus.NOT_FOUND),
        )

        for client, status in users_statuses:

            for url in (
                'notes:edit',
                'notes:delete',
                'notes:detail',
            ):
                with self.subTest():
                    response = client.get(reverse(url, args=(self.note.slug,)))
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
