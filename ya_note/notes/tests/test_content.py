from django.contrib.auth import get_user_model

from .fixtures import Fixtures

User = get_user_model()


class TestContent(Fixtures):

    NOTES_CREATED = 5

    def test_specific_note_in_notes_list(self):
        """
        Отдельная заметка передаётся на страницу со списком
        заметок в списке object_list в словаре context.
        """
        response = self.author_logged.get(self.URL_NOTES_LIST)
        self.assertIn(self.note, response.context['object_list'])

    def test_different_authors_notes(self):
        """
        В список заметок одного пользователя не
        попадают заметки другого пользователя.
        """
        response = self.reader_logged.get(self.URL_NOTES_LIST)
        reader_notes_list = response.context['object_list']

        self.assertEqual(self.note in reader_notes_list, False)
        self.assertNotIsInstance(self.note, tuple(reader_notes_list))

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
