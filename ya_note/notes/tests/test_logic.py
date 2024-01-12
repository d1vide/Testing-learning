from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestLogic(TestCase):
    NOTE_TITLE = 'Название'
    NOTE_TEXT = 'Текст'
    NOTE_SLUG = 'slugnote'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.auth_client_author = Client()
        cls.auth_client_author.force_login(cls.author)
        cls.form_data = {'title': cls.NOTE_TITLE,
                         'text': cls.NOTE_TEXT,
                         'slug': cls.NOTE_SLUG}
        cls.url = reverse('notes:add')

    def test_auth_user_can_create_note(self):
        self.auth_client_author.post(self.url, self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, self.NOTE_SLUG)

    def test_anon_user_cannot_create_note(self):
        login_url = reverse('users:login')
        response = self.client.post(self.url, self.form_data)
        self.assertEqual(Note.objects.count(), 0)
        redirect_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, redirect_url)

    def test_two_same_slugs(self):
        self.auth_client_author.post(self.url, self.form_data)
        note = Note.objects.get()
        response = self.auth_client_author.post(self.url, self.form_data)
        self.assertFormError(response,
                             'form',
                             'slug',
                             errors=(note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_slug_auto(self):
        self.form_data.pop('slug')
        response = self.auth_client_author.post(self.url, self.form_data)
        redirect_url = reverse('notes:success')
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(self.form_data['title']))


class TestEditDeleteNote(TestCase):
    NEW_NOTE_TITLE = 'Название new'
    NEW_NOTE_TEXT = 'Текст new'
    NEW_NOTE_SLUG = 'slugnotenew'
    NOTE_TITLE = 'Название'
    NOTE_TEXT = 'Текст'
    NOTE_SLUG = 'slugnote'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.auth_client_author = Client()
        cls.auth_client_author.force_login(cls.author)
        cls.form_data = {'title': cls.NEW_NOTE_TITLE,
                         'text': cls.NEW_NOTE_TEXT,
                         'slug': cls.NEW_NOTE_SLUG}
        cls.reader = User.objects.create(username='Читатель')
        cls.auth_client_reader = Client()
        cls.auth_client_reader.force_login(cls.reader)
        cls.note = Note.objects.create(title=cls.NOTE_TITLE,
                                       text=cls.NOTE_TEXT,
                                       author=cls.author,
                                       slug=cls.NOTE_SLUG)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.redirect_url = reverse('notes:success')

    def test_author_can_delete_note(self):
        response = self.auth_client_author.delete(self.delete_url)
        self.assertRedirects(response, self.redirect_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_reader_can_not_delete_note(self):
        response = self.auth_client_reader.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        response = self.auth_client_author.post(self.edit_url,
                                                data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NEW_NOTE_SLUG)

    def test_reader_can_not_edit_note(self):
        response = self.auth_client_reader.post(self.edit_url,
                                                data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
