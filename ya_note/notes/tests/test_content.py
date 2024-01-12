from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(title='Название',
                                       text='Текст',
                                       author=cls.author,
                                       slug='noteslug')
        cls.reader = User.objects.create(username='Юзер без заметок')

    def test_note_in_context(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertIn(self.note, response.context['object_list'])

    def test_notes_list_for_other_user(self):
        self.client.force_login(self.reader)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_form_in_context_for_add_and_edit(self):
        self.client.force_login(self.author)
        for name, arg in (('notes:add', None), ('notes:edit', self.note.slug)):
            with self.subTest(name=name):
                if arg is None:
                    url = reverse(name)
                else:
                    url = reverse(name, args=(arg, ))
                response = self.client.get(url)
                self.assertIn('form', response.context)
