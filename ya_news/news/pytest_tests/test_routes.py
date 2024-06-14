from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

'''Тесты доступности страниц.'''
@pytest.mark.parametrize(
    'name',
    (
        'news:home',
    )
)
def test_main_page_availability_for_anonymous_user(client, db, name):
    '''Главная страница доступна анонимному пользователю.'''
    assert client.get(reverse(name)).status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_for_args')),
    )
)
def test_news_pages_availability_for_anonymous_user(client, db, name, args):
    '''Страница отдельной новости доступна анонимному пользователю.'''
    assert client.get(reverse(name, args=args)).status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    (
        ('users:login'),
        ('users:logout'),
        ('users:signup'),
    )
)
def test_users_pages_availability_for_anonymous_user(client, db, name):
    '''Страницы регистрации пользователей,
       входа в учётную запись и выхода из
       неё доступны анонимным пользователям.'''
    assert client.get(reverse(name)).status_code == HTTPStatus.OK


'''Тесты комментов.'''
@pytest.mark.parametrize(
    'name',
    (
        ('news:delete'),
        ('news:edit'),
    )
)
def test_pages_availability_for_author(author_client, comment_id_for_args, name):
    '''Страницы удаления и редактирования
       комментария доступны автору комментария.'''
    assert author_client.get(
        reverse(name, args=comment_id_for_args)
    ).status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
    parametrized_client,
    expected_status,
    name,
    comment_id_for_args,
):
    '''Авторизованный пользователь не может зайти на
       страницы редактирования или удаления чужих 
       комментариев (возвращается ошибка 404).'''

    assert parametrized_client.get(
        reverse(name, args=comment_id_for_args)
    ).status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirects_for(client, db, name, comment_id_for_args):
    '''При попытке перейти на страницу редактирования
       или удаления комментария анонимный пользователь
       перенаправляется на страницу авторизации.'''
    login_url = reverse('users:login')
    url = reverse(name, args=comment_id_for_args)
    assertRedirects(client.get(url), f'{login_url}?next={url}')
