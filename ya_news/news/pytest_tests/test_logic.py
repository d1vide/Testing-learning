from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, detail_url):
    response = client.post(detail_url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client,
                                 form_data,
                                 news,
                                 author,
                                 detail_url):
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news == news
    assert new_comment.author == author
    assert new_comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, detail_url):
    bad_words_data = {'text': f'Текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment, new_form_data):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data=new_form_data)
    url_to_comment = (reverse('news:detail', args=(comment.news.id,))
                      + '#comments')
    assertRedirects(response, url_to_comment)
    comment.refresh_from_db()
    assert comment.text == new_form_data['text']


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)
    url_to_comment = (reverse('news:detail', args=(comment.news.id,))
                      + '#comments')
    assertRedirects(response, url_to_comment)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_reader_can_not_edit_comment(reader_client, comment, new_form_data):
    url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(url, data=new_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get()
    comment.refresh_from_db()
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author
    assert comment_from_db.text == comment.text


@pytest.mark.django_db
def test_reader_can_not_delete_comment(reader_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
