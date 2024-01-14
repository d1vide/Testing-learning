from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

NOTE_SLUG = 'slugnote'
URL_HOME = reverse('notes:home')
URL_ADD = reverse('notes:add')
URL_LIST = reverse('notes:list')
URL_SUCCESS = reverse('notes:success')
URL_DETAIL = reverse('notes:detail', args=(NOTE_SLUG,))
URL_DELETE = reverse('notes:delete', args=(NOTE_SLUG,))
URL_EDIT = reverse('notes:edit', args=(NOTE_SLUG,))


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Юзер читающий заметки')
        cls.author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(title='Название',
                                       text='Текст',
                                       author=cls.author,
                                       slug=NOTE_SLUG)

    def test_home_page(self):
        response = self.client.get(URL_HOME)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability(self):
        urls = (
            URL_ADD,
            URL_LIST,
            URL_SUCCESS,
        )
        self.client.force_login(self.reader)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_view_delete_update(self):
        users_statuses = (
            (self.reader, HTTPStatus.NOT_FOUND),
            (self.author, HTTPStatus.OK),
        )
        urls = (
            URL_DETAIL,
            URL_DELETE,
            URL_EDIT,
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for url in urls:
                with self.subTest(user=user, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            URL_DETAIL,
            URL_DELETE,
            URL_EDIT,
            URL_ADD,
            URL_LIST,
            URL_SUCCESS,
        )
        login_url = reverse('users:login')
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(response, redirect_url)

    def test_availability_auth_pages(self):
        urls = (
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            url = reverse(name)
            for user in (None, self.reader):
                with self.subTest(name=name, user=user):
                    if user is not None:
                        self.client.force_login(user)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.client.logout()
