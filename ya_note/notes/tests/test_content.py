from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

from .fixtures import Fixtures

User = get_user_model()


class TestContent(Fixtures):

    NOTES_CREATED = 5

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.notes = Note.objects.bulk_create(
            Note(
                title=f'Новость {index}',
                slug=f'slug_{index}',
                text='Просто текст.',
                author=cls.author,
            )
            for index in range(cls.NOTES_CREATED)
        )
        cls.URL_NOTES_EDIT = reverse('notes:edit', args=(cls.notes[0].slug,))

    def test_specific_note_in_notes_list(self):
        """
        Отдельная заметка передаётся на страницу со списком
        заметок в списке object_list в словаре context.
        """
        response = self.author_logged.get(self.URL_NOTES_LIST)
        news = response.context['object_list']
        self.assertIn(news[0], news)

    def test_different_authors_notes(self):
        """
        В список заметок одного пользователя не
        попадают заметки другого пользователя.
        """
        response = self.author_logged.get(self.URL_NOTES_LIST)
        author_notes_list = response.context['object_list']

        response = self.reader_logged.get(self.URL_NOTES_LIST)
        reader_notes_list = response.context['object_list']

        self.assertEqual(author_notes_list[0] in reader_notes_list, False)

    def test_forms_are_in_pages(self):
        """На страницы создания и редактирования заметки передаются формы."""
        for url in (
            self.URL_NOTES_ADD,
            self.URL_NOTES_EDIT
        ):
            with self.subTest():
                self.assertIn(
                    'form', self.author_logged.get(url).context
                )
