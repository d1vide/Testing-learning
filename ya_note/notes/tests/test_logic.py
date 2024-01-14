from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()

NOTE_SLUG = 'slugnote'
URL_ADD = reverse('notes:add')
URL_SUCCESS = reverse('notes:success')
URL_DELETE = reverse('notes:delete', args=(NOTE_SLUG,))
URL_EDIT = reverse('notes:edit', args=(NOTE_SLUG,))
URL_LOGIN = reverse('users:login')


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

    def test_auth_user_can_create_note(self):
        self.auth_client_author.post(URL_ADD, self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, self.NOTE_SLUG)

    def test_anon_user_cannot_create_note(self):
        response = self.client.post(URL_ADD, self.form_data)
        self.assertEqual(Note.objects.count(), 0)
        redirect_url = f'{URL_LOGIN}?next={URL_ADD}'
        self.assertRedirects(response, redirect_url)

    def test_two_same_slugs(self):
        self.auth_client_author.post(URL_ADD, self.form_data)
        note = Note.objects.get()
        response = self.auth_client_author.post(URL_ADD, self.form_data)
        self.assertFormError(response,
                             'form',
                             'slug',
                             errors=(note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_slug_auto(self):
        self.form_data.pop('slug')
        response = self.auth_client_author.post(URL_ADD, self.form_data)
        self.assertRedirects(response, URL_SUCCESS)
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

    def test_author_can_delete_note(self):
        response = self.auth_client_author.delete(URL_DELETE)
        self.assertRedirects(response, URL_SUCCESS)
        self.assertEqual(Note.objects.count(), 0)

    def test_reader_can_not_delete_note(self):
        response = self.auth_client_reader.delete(URL_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        response = self.auth_client_author.post(URL_EDIT,
                                                data=self.form_data)
        self.assertRedirects(response, URL_SUCCESS)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NEW_NOTE_SLUG)

    def test_reader_can_not_edit_note(self):
        response = self.auth_client_reader.post(URL_EDIT,
                                                data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
