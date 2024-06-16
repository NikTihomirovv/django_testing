from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

TEST_TEXT = {'text': 'Тестовый текст'}
pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_note(
    client,
    news,
    url_news_detail,
    url_user_login
):
    """Анонимный пользователь не может отправить комментарий."""
    Comment.objects.all().delete()
    comments_befort_test = Comment.objects.count()
    response = client.post(url_news_detail, data=TEST_TEXT)
    assertRedirects(response, f'{url_user_login}?next={url_news_detail}')
    assert Comment.objects.count() == comments_befort_test


def test_user_can_create_comment(author_client, author, news, url_news_detail):
    """Авторизованный пользователь может отправить комментарий."""
    Comment.objects.all().delete()
    comments_befort_test = Comment.objects.count()
    response = author_client.post(url_news_detail, data=TEST_TEXT)
    assertRedirects(response, f'{url_news_detail}#comments')
    assert Comment.objects.count() == comments_befort_test + 1

    new_comment = Comment.objects.get()
    assert new_comment.text == TEST_TEXT['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_bad_words(author_client, news, url_news_detail):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    comments_befort_test = Comment.objects.count()
    response = author_client.post(
        url_news_detail,
        {'text': f'Текст {choice(BAD_WORDS)}'}
    )
    assert Comment.objects.count() == comments_befort_test
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )


def test_author_can_delete_comment(
    author_client, news, comment,
    url_news_detail, url_comment_delete
):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_befort_test = Comment.objects.count()
    response = author_client.delete(url_comment_delete)
    assertRedirects(response, f'{url_news_detail}#comments')
    assert Comment.objects.count() == comments_befort_test - 1


def test_author_can_edit_comment(
    author_client,
    news,
    comment,
    url_news_detail,
    url_comment_edit
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    comments_befort_test = Comment.objects.count()
    response = author_client.post(
        url_comment_edit,
        data=TEST_TEXT
    )
    assertRedirects(response, f'{url_news_detail}#comments')
    assert Comment.objects.count() == comments_befort_test

    comment_db = Comment.objects.get(id=comment.id)
    assert comment_db.text == TEST_TEXT['text']
    assert comment_db.news == comment.news
    assert comment_db.author == comment.author


def test_user_cant_delete_comment(reader_client, comment, url_comment_delete):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comments_befort_test = Comment.objects.count()
    response = reader_client.delete(url_comment_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_befort_test


def test_user_cant_edit_comment(reader_client, comment, url_comment_edit):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = reader_client.post(
        url_comment_edit,
        data=TEST_TEXT)
    comment_db = Comment.objects.get(id=comment.id)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment_db.text == comment.text
    assert comment_db.news == comment.news
    assert comment_db.author == comment.author
