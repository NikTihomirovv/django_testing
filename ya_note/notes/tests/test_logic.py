from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.text import slugify

from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Залогиненный юзер')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

        cls.note = Note.objects.create(
            title = 'test_title',
            text = 'test_text',
            slug = 'test_slug',
            author = cls.author,
        )

        cls.form_data = {
            'title': 'test_form_title',
            'text': 'test_form_text',
            'slug': 'test_form_slug',
        }

        cls.NOTE_BEFORE_REQUEST = Note.objects.count()
        cls.NOTE_ADD = reverse('notes:add')
        cls.NOTE_SUCCESS = reverse('notes:success')
    
    def test_note_creation_by_logged_user(self):
        '''Залогиненный пользователь может создать заметку.'''
        self.assertRedirects(
            self.auth_client.post(self.NOTE_ADD,
            data=self.form_data),
            self.NOTE_SUCCESS
        )

    def test_note_creation_by_annonymous_user(self):
        '''Анонимный пользователь не может создать заметку.'''
        self.client.post(self.NOTE_ADD, data=self.form_data)
        self.assertEqual(Note.objects.count(), self.NOTE_BEFORE_REQUEST)

    def test_similar_slug(self):
        '''Невозможно создать две заметки с одинаковым slug.'''

        with self.assertRaises(IntegrityError) as error:
            Note.objects.create(
                title = 'test_title',
                text = 'test_text',
                slug = 'test_slug',
                author = self.author,
            )

        self.assertEqual(str(error.exception), 'UNIQUE constraint failed: notes_note.slug')

    def test_auto_slug(self):
        '''Если при создании заметки не заполнен slug,
        то он формируется автоматически,
        с помощью функции pytils.translit.slugify.'''

        title_for_slug = 'test_title_for_sugify'
        Note.objects.create(
                title = title_for_slug,
                text = 'test_text',
                slug = '',
                author = self.author,
            )
        
        self.assertTrue(self.client.get('notes:detail', args=slugify(title_for_slug)))


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
            title = 'test_title',
            text = 'test_text',
            slug = 'test_slug',
            author = cls.author,
        )

        cls.form_data = {
            'title': 'test_form_title',
            'text': 'test_form_text',
            'slug': 'test_form_slug',
        }

        cls.NOTE_EDIT = reverse('notes:edit', args=(cls.note.slug,))
        cls.NOTE_DELETE = reverse('notes:delete', args=(cls.note.slug,))
        cls.NOTE_SUCCESS = reverse('notes:success', args=None)

    def test_user_can_edit_his_notes(self):
        '''Пользователь может редактировать свои заметки.'''
        self.assertRedirects(
            self.author_client.post(self.NOTE_EDIT, data=self.form_data),
            self.NOTE_SUCCESS
        )

        self.note.refresh_from_db()
        self.assertEqual(self.note.text, 'test_form_text')
        self.assertEqual(self.note.title, 'test_form_title')
        

    def test_user_can_delete_his_notes(self):
        '''Пользователь может удалять свои заметки.'''
        self.assertRedirects(
            self.author_client.delete(self.NOTE_DELETE),
            self.NOTE_SUCCESS
        )
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_edit_other_notes(self):
        '''Пользователь неможет редактировать чужие заметки.'''
        response = self.reader_client.post(self.NOTE_EDIT, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, 'test_text')
        self.assertEqual(self.note.title, 'test_title')

    def test_user_cant_delete_other_notes(self):
        '''Пользователь неможет удалять чужие заметки.'''
        response = self.reader_client.delete(self.NOTE_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
