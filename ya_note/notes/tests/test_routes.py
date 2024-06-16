from http import HTTPStatus

from .fixtures import Fixtures


class TestRoutes(Fixtures):

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
