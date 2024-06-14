from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    NOTES_URL = reverse('notes:list')
    NOTES_CREATED = 5

    @classmethod
    def setUpTestData(cls):

        cls.author_1 = User.objects.create(username='Автор_1')
        cls.author_2 = User.objects.create(username='Автор_2')

        cls.notes = Note.objects.bulk_create(
            Note(
                title=f'Новость {index}',
                slug=f'slug_{index}',
                text='Просто текст.',      
                author=cls.author_1,
            )
            for index in range(cls.NOTES_CREATED)
        )

    def test_specific_note_in_notes_list(self):
        '''Отдельная заметка передаётся на страницу со списком
           заметок в списке object_list в словаре context.'''
   
        self.client.force_login(self.author_1)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        first_note = object_list[0]
        self.assertIn(first_note, object_list)

    def test_different_authors_notes(self):
        '''В список заметок одного пользователя не
           попадают заметки другого пользователя.'''
        
        self.client.force_login(self.author_1)
        response = self.client.get(self.NOTES_URL)
        first_author_notes_count = len(response.context['object_list'])

        self.client.force_login(self.author_2)
        response = self.client.get(self.NOTES_URL)
        second_author_notes_count = len(response.context['object_list'])

        self.assertNotEqual(first_author_notes_count, second_author_notes_count)


class TestAddAndEdit(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='test_title',
            slug='test_slug',
            text='test_text',
            author=cls.author
        )

    def test_forms_are_in_pages(self):
        '''На страницы создания и редактирования заметки передаются формы.'''

        self.client.force_login(self.author)
        for url, args in (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        ):
            with self.subTest():
                self.assertIn(
                    'form', self.client.get(reverse(url, args=args)).context
                )

        
