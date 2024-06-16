from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.utils.text import slugify

from notes.forms import WARNING
from notes.models import Note

from .fixtures import Fixtures

User = get_user_model()


class TestNoteCreation(Fixtures):

    def test_note_creation_by_logged_user(self):
        """Залогиненный пользователь может создать заметку."""
        NOTES_BEFORE_REQUEST = Note.objects.count()
        self.assertRedirects(
            self.author_logged.post(self.URL_NOTES_ADD, data=self.form_data),
            self.URL_NOTES_SUCCESS
        )
        self.assertEqual(Note.objects.count(), NOTES_BEFORE_REQUEST + 1)
        note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])

    def test_note_creation_by_annonymous_user(self):
        """Анонимный пользователь не может создать заметку."""
        NOTES_BEFORE_REQUEST = Note.objects.count()
        self.client.post(self.URL_NOTES_ADD, data=self.form_data)
        self.assertEqual(Note.objects.count(), NOTES_BEFORE_REQUEST)

    def test_similar_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        NOTES_BEFORE_REQUEST = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_logged.post(
            self.URL_NOTES_ADD,
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
        response = self.author_logged.post(
            self.URL_NOTES_ADD,
            data=self.form_data
        )

        self.assertRedirects(response, self.URL_NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), NOTES_BEFORE_REQUEST + 1)
        self.assertEqual(
            Note.objects.get(id=NOTES_BEFORE_REQUEST + 1).slug,
            slugify(self.form_data['title'])
        )

    def test_user_can_edit_his_notes(self):
        """Пользователь может редактировать свои заметки."""
        self.assertRedirects(
            self.author_logged.post(self.URL_NOTES_EDIT, data=self.form_data),
            self.URL_NOTES_SUCCESS
        )

        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_user_can_delete_his_notes(self):
        """Пользователь может удалять свои заметки."""
        NOTES_BEFORE_REQUEST = Note.objects.count()
        self.assertRedirects(
            self.author_logged.delete(self.URL_NOTES_DELETE),
            self.URL_NOTES_SUCCESS
        )
        self.assertEqual(Note.objects.count(), NOTES_BEFORE_REQUEST - 1)

    def test_user_cant_edit_other_notes(self):
        """Пользователь неможет редактировать чужие заметки."""
        response = self.reader_logged.post(
            self.URL_NOTES_EDIT,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        new_note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.text, new_note.text)
        self.assertEqual(self.note.title, new_note.title)
        self.assertEqual(self.note.slug, new_note.slug)
        self.assertEqual(self.note.author, new_note.author)

    def test_user_cant_delete_other_notes(self):
        """Пользователь неможет удалять чужие заметки."""
        NOTES_BEFORE_REQUEST = Note.objects.count()
        response = self.reader_logged.delete(self.URL_NOTES_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), NOTES_BEFORE_REQUEST)
