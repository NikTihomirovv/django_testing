from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.text import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Залогиненный юзер')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

        cls.note = Note.objects.create(
            title='test_title',
            text='test_text',
            slug='test_slug',
            author=cls.author,
        )

        cls.form_data = {
            'title': 'test_form_title',
            'text': 'test_form_text',
            'slug': 'test_form_slug',
        }

        cls.NOTE_ADD = reverse('notes:add')
        cls.NOTE_SUCCESS = reverse('notes:success')

    def test_note_creation_by_logged_user(self):
        """Залогиненный пользователь может создать заметку."""
        NOTES_BEFORE_REQUEST = Note.objects.count()
        self.assertRedirects(
            self.auth_client.post(self.NOTE_ADD, data=self.form_data),
            self.NOTE_SUCCESS
        )
        self.assertEqual(Note.objects.count(), NOTES_BEFORE_REQUEST + 1)

    def test_note_creation_by_annonymous_user(self):
        """Анонимный пользователь не может создать заметку."""
        NOTES_BEFORE_REQUEST = Note.objects.count()
        self.client.post(self.NOTE_ADD, data=self.form_data)
        self.assertEqual(Note.objects.count(), NOTES_BEFORE_REQUEST)

    def test_similar_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        NOTES_BEFORE_REQUEST = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.auth_client.post(
            self.NOTE_ADD,
            data=self.form_data
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), NOTES_BEFORE_REQUEST)

    def test_auto_slug(self):
        """
        Если при создании заметки не заполнен slug,
        то он формируется автоматически,
        с помощью функции pytils.translit.slugify.
        """
        NOTES_BEFORE_REQUEST = Note.objects.count()
        self.form_data['slug'] = ''
        response = self.auth_client.post(
            self.NOTE_ADD,
            data=self.form_data
        )
        self.assertTrue(
            self.client.get('notes:detail', args=slugify('title'))
        )
        self.assertRedirects(response, self.NOTE_SUCCESS)
        self.assertEqual(Note.objects.count(), NOTES_BEFORE_REQUEST + 1)


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='test_author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='test_reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='test_title',
            text='test_text',
            slug='test_slug',
            author=cls.author,
        )

        cls.form_data = {
            'title': 'test_form_title',
            'text': 'test_form_text',
            'slug': 'test_form_slug',
            'author': cls.author,
        }

        cls.NOTE_EDIT = reverse('notes:edit', args=(cls.note.slug,))
        cls.NOTE_DELETE = reverse('notes:delete', args=(cls.note.slug,))
        cls.NOTE_SUCCESS = reverse('notes:success', args=None)

    def test_user_can_edit_his_notes(self):
        """Пользователь может редактировать свои заметки."""
        self.assertRedirects(
            self.author_client.post(self.NOTE_EDIT, data=self.form_data),
            self.NOTE_SUCCESS
        )

        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.form_data['author'])

    def test_user_can_delete_his_notes(self):
        """Пользователь может удалять свои заметки."""
        NOTES_BEFORE_REQUEST = Note.objects.count()
        self.assertRedirects(
            self.author_client.delete(self.NOTE_DELETE),
            self.NOTE_SUCCESS
        )
        self.assertEqual(Note.objects.count(), NOTES_BEFORE_REQUEST - 1)

    def test_user_cant_edit_other_notes(self):
        """Пользователь неможет редактировать чужие заметки."""
        response = self.reader_client.post(self.NOTE_EDIT, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        new_note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.text, new_note.text)
        self.assertEqual(self.note.title, new_note.title)
        self.assertEqual(self.note.slug, new_note.slug)
        self.assertEqual(self.note.author, new_note.author)

    def test_user_cant_delete_other_notes(self):
        """Пользователь неможет удалять чужие заметки."""
        NOTES_BEFORE_REQUEST = Note.objects.count()
        response = self.reader_client.delete(self.NOTE_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), NOTES_BEFORE_REQUEST)
