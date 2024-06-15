from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    NOTES_CREATED = 5

    @classmethod
    def setUpTestData(cls):

        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_logged = Client()
        cls.reader_logged = Client()
        cls.author_logged.force_login(cls.author)
        cls.reader_logged.force_login(cls.reader)

        cls.notes = Note.objects.bulk_create(
            Note(
                title=f'Новость {index}',
                slug=f'slug_{index}',
                text='Просто текст.',
                author=cls.author,
            )
            for index in range(cls.NOTES_CREATED)
        )

        cls.URL_NOTE_LIST = reverse('notes:list')

    def test_specific_note_in_notes_list(self):
        """
        Отдельная заметка передаётся на страницу со списком
        заметок в списке object_list в словаре context.
        """
        response = self.author_logged.get(self.URL_NOTE_LIST)
        news_list = response.context['object_list']
        self.assertIn(news_list[0], news_list)

    def test_different_authors_notes(self):
        """
        В список заметок одного пользователя не
        попадают заметки другого пользователя.
        """
        response = self.author_logged.get(self.URL_NOTE_LIST)
        author_notes_list = response.context['object_list']

        response = self.reader_logged.get(self.URL_NOTE_LIST)
        reader_notes_list = response.context['object_list']

        self.assertEqual(author_notes_list[0] in reader_notes_list, False)


class TestAddAndEdit(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_logged = Client()
        cls.author_logged.force_login(cls.author)

        cls.note = Note.objects.create(
            title='test_title',
            slug='test_slug',
            text='test_text',
            author=cls.author
        )

        cls.URL_NOTE_ADD = reverse('notes:add')
        cls.URL_NOTE_EDIT = reverse('notes:edit', args=(cls.note.slug,))

    def test_forms_are_in_pages(self):
        """На страницы создания и редактирования заметки передаются формы."""
        for url in (
            self.URL_NOTE_ADD,
            self.URL_NOTE_EDIT
        ):
            with self.subTest():
                self.assertIn(
                    'form', self.author_logged.get(url).context
                )
