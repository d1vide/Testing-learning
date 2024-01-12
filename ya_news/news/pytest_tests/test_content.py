import pytest
from django.conf import settings


@pytest.mark.usefixtures('news_list')
@pytest.mark.django_db
def test_news_on_page_count(client, home_url):
    response = client.get(home_url)
    news_count = len(response.context['object_list'])
    print(news_count)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('news_list')
@pytest.mark.django_db
def test_sort_news(client, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('comment_list')
@pytest.mark.django_db
def test_sort_comments(client, news, detail_url):
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_times = [comm.created for comm in all_comments]
    sorted_times = sorted(all_times)
    assert all_times == sorted_times


@pytest.mark.usefixtures('news')
@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.usefixtures('news')
@pytest.mark.django_db
def test_authorized_client_has_form(client, author, detail_url):
    client.force_login(author)
    response = client.get(detail_url)
    assert 'form' in response.context
