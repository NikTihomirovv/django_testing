from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Фикстура для создания объекта автора заметки."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    """Фикстура для создания объекта читателя заметки."""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    """Клиент залогиненого автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Клиент читателя."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    """Фикстура для создания объекта новости."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment(news, author):
    """Фикстура для создания объекта коментария."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст коментария',
    )
    return comment


@pytest.fixture
def news_list():
    """Создает 11 новостей."""
    today = datetime.today()

    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст',
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def ten_comments(news, author):
    """Создает 10 коментов к новости."""
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )

        comment.created = timezone.now() + timedelta(days=index)
        comment.save()


# Fixtures for reverse


@pytest.fixture
def url_news_home():
    return reverse('news:home')


@pytest.fixture
def url_news_detail(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_comment_edit(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def url_comment_delete(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def url_user_login():
    return reverse('users:login')


@pytest.fixture
def url_user_logout():
    return reverse('users:logout')


@pytest.fixture
def url_user_signup():
    return reverse('users:signup')
