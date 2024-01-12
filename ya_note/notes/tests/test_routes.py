from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Юзер читающий заметки')
        cls.author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(title='Название',
                                       text='Текст',
                                       author=cls.author,
                                       slug='noteslug')

    def test_home_page(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability(self):
        urls = (
            'notes:add',
            'notes:list',
            'notes:success',
        )
        self.client.force_login(self.reader)
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_view_delete_update(self):
        users_statuses = (
            (self.reader, HTTPStatus.NOT_FOUND),
            (self.author, HTTPStatus.OK),
        )
        urls = (
            'notes:detail',
            'notes:delete',
            'notes:edit',
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', self.note.slug),
            ('notes:detail', self.note.slug),
            ('notes:delete', self.note.slug),
            ('notes:success', None),
            ('notes:list', None),
        )
        login_url = reverse('users:login')
        for name, slug in urls:
            with self.subTest(name=name):
                if slug is None:
                    url = reverse(name)
                else:
                    url = reverse(name, args=(slug,))
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
