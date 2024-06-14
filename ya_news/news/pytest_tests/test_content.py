import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_news_list_in_home_page(news_list, client):
    """Количество новостей на главной странице — не более 10."""
    assert len(client.get(reverse('news:home')).context['object_list']) == 10


@pytest.mark.django_db
def test_news_order(news_list, client):
    """
    Новости отсортированы от самой свежей к
    самой старой. Свежие новости в начале списка.
    """
    object_list = client.get(reverse('news:home')).context['object_list']
    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, news, ten_comments):
    """
    Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    news = client.get(reverse('news:detail', args=(news.id,))).context['news']
    all_comments = news.comment_set.all()
    all_date_created = [comment.created for comment in all_comments]
    assert all_date_created == sorted(all_date_created)


@pytest.mark.django_db
def test_form_availability_for_user(author_client, news, form_data):
    """
    Авторизованному пользователю доступна форма для отправки
    комментария на странице отдельной новости.
    """
    response = author_client.get(
        reverse('news:detail', args=(news.id,)), data=form_data
    )
    assert 'form' in response.context


@pytest.mark.django_db
def test_form_is_nt_available_for_anon_user(client, news):
    """
    Анонимному пользователю недоступна форма для
    отправки комментария на странице отдельной новости.
    """
    assert 'form' not in client.get(
        reverse('news:detail', args=(news.id,))
    ).context
