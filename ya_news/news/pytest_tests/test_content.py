import pytest
from django.conf import settings

from news.forms import CommentForm

TEST_TEXT = {'text': 'Тестовый текст'}
pytestmark = pytest.mark.django_db


def test_news_list_in_home_page(news_list, client, url_news_home):
    """Количество новостей на главной странице — не более 10."""
    assert client.get(
        url_news_home
    ).context['object_list'].count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(news_list, client, url_news_home):
    """
    Новости отсортированы от самой свежей к
    самой старой. Свежие новости в начале списка.
    """
    all_dates = [news.date for news in client.get(
        url_news_home
    ).context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, news, ten_comments, url_news_detail):
    """
    Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    news = client.get(url_news_detail).context['news']
    all_comments = news.comment_set.all()
    all_date_created = [comment.created for comment in all_comments]
    assert all_date_created == sorted(all_date_created)


def test_form_availability_for_user(author_client, news, url_news_detail):
    """
    Авторизованному пользователю доступна форма для отправки
    комментария на странице отдельной новости.
    """
    response = author_client.get(
        url_news_detail, data=TEST_TEXT
    )
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_form_is_nt_available_for_anon_user(client, news, url_news_detail):
    """
    Анонимному пользователю недоступна форма для
    отправки комментария на странице отдельной новости.
    """
    assert 'form' not in client.get(
        url_news_detail,
    ).context
