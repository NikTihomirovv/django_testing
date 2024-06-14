from http import HTTPStatus
from random import choice

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data, news):
    '''Анонимный пользователь не может отправить комментарий.'''
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    assertRedirects(response, f'{login_url}?next={url}')
    assert Comment.objects.count() == 0

@pytest.mark.django_db
def test_user_can_create_comment(author_client, author, form_data, news):
    '''Авторизованный пользователь может отправить комментарий.'''
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1

    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.django_db
def test_bad_words(author_client, news):
    '''Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.'''

    response = author_client.post(
        reverse('news:detail', args=(news.id,)),
        {'text': f'Текст {choice(BAD_WORDS)}'}
    )

    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )

    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, news, comment):
    '''Авторизованный пользователь может удалять свои комментарии.'''
    comment_url = reverse('news:detail', args=(news.id,)) + '#comments'
    response = author_client.delete(
        reverse('news:delete', args=(comment.id,))
    )
    assertRedirects(response, comment_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, news, form_data, comment):
    '''Авторизованный пользователь может редактировать свои комментарии.'''
    comment_url = reverse('news:detail', args=(news.id,)) + '#comments'
    response = author_client.post(
        reverse('news:edit', args=(comment.id,)),
        data=form_data
    )
    assertRedirects(response, comment_url)
    assert Comment.objects.count() == 1


@pytest.mark.django_db  
def test_user_cant_delete_comment(reader_client, comment):
    '''Авторизованный пользователь не может удалять чужие комментарии.'''
    response = reader_client.delete(
        reverse('news:delete', args=(comment.id,))
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_user_cant_edit_comment(reader_client, form_data, comment):
    '''Авторизованный пользователь не может редактировать чужие комментарии.'''
    response = reader_client.post(
        reverse('news:edit', args=(comment.id,)),
        data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
