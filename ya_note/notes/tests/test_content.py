from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()

NOTE_SLUG = 'slugnote'
URL_ADD = reverse('notes:add')
URL_LIST = reverse('notes:list')
URL_EDIT = reverse('notes:edit', args=(NOTE_SLUG,))


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(title='Название',
                                       text='Текст',
                                       author=cls.author,
                                       slug=NOTE_SLUG)
        cls.reader = User.objects.create(username='Юзер без заметок')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_note_in_context(self):
        response = self.author_client.get(URL_LIST)
        self.assertIn(self.note, response.context['object_list'])

    def test_notes_list_for_other_user(self):
        response = self.reader_client.get(URL_LIST)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_form_in_context_for_add_and_edit(self):
        for url in (URL_ADD, URL_EDIT):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
