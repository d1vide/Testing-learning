from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from news.models import News, Comment


COUNT_TEST_COMMENTS = 5


@pytest.fixture
def news():
    news = News.objects.create(title='Название', text='Текст')
    return news


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(news=news,
                                     text='Текст комментария',
                                     author=author)
    return comment


@pytest.fixture
def reader_client(django_user_model, client):
    reader = django_user_model.objects.create(username='Читатель')
    client.force_login(reader)
    return client


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(news):
    return reverse('news:edit', args=(news.id,))


@pytest.fixture
def delete_url(news):
    return reverse('news:delete', args=(news.id,))


@pytest.fixture
def news_list():
    today = datetime.today()
    all_news = [
        News(title=f'Новость {index}',
             text='Текст',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comment_list(news, author):
    now = timezone.now()
    all_comments = []
    for index in range(COUNT_TEST_COMMENTS):
        comment = Comment(news=news, author=author, text='Текст')
        comment.created = now + timedelta(days=index)
        comment.save()
        all_comments.append(comment)
    return all_comments


@pytest.fixture
def form_data():
    return {
        'text': 'Текст комментария',
    }


@pytest.fixture
def new_form_data():
    return {
        'text': 'Новый комментарий',
    }
