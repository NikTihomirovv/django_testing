from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


def test_main_page_availability_for_anonymous_user(client, url_news_home):
    """Главная страница доступна анонимному пользователю."""
    assert client.get(url_news_home).status_code == HTTPStatus.OK


def test_news_pages_availability_for_anonymous_user(
        client,
        news,
        url_news_detail
):
    """Страница отдельной новости доступна анонимному пользователю."""
    assert client.get(url_news_detail).status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'reverse_url',
    (
        pytest.lazy_fixture('url_user_login'),
        pytest.lazy_fixture('url_user_logout'),
        pytest.lazy_fixture('url_user_signup'),
    )
)
def test_users_pages_availability_for_anonymous_user(client, reverse_url):
    """
    Страницы регистрации пользователей,
       входа в учётную запись и выхода из
       неё доступны анонимным пользователям.
    """
    assert client.get(reverse_url).status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, expected_status',
    (
        (
            pytest.lazy_fixture('url_comment_edit'),
            pytest.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('url_comment_delete'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        )
    ),
)
def test_pages_availability_for_different_users(
    reverse_url,
    parametrized_client,
    expected_status,
    comment,
    author_client
):
    """
    Авторизованный пользователь не может зайти на
    страницы редактирования или удаления чужих
    комментариев (возвращается ошибка 404).

    Страницы удаления и редактирования
    комментария доступны автору комментария.
    """
    assert parametrized_client.get(reverse_url).status_code == expected_status
    assert author_client.get(reverse_url).status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'reverse_url',
    (
        pytest.lazy_fixture('url_comment_edit'),
        pytest.lazy_fixture('url_comment_delete'),
    )
)
def test_redirects_for(client, reverse_url, comment, url_user_login):
    """
    При попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь
    перенаправляется на страницу авторизации.
    """
    assertRedirects(
        client.get(reverse_url),
        f'{url_user_login}?next={reverse_url}'
    )
