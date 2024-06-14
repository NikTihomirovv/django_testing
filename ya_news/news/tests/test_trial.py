# # news/tests/test_trial.py
# from django.test import TestCase
# from news.models import News
# from django.contrib.auth import get_user_model
# from django.test import Client, TestCase

# # Получаем модель пользователя.
# User = get_user_model()


# class TestNews(TestCase):

#     # В методе класса setUpTestData создаём тестовые объекты.
#     # Оборачиваем метод соответствующим декоратором.    
#     @classmethod
#     def setUpTestData(cls):
#         # Стандартным методом Django ORM create() создаём объект класса.
#         # Присваиваем объект атрибуту класса: назовём его news.
#         cls.news = News.objects.create(
#             title='Заголовок новости',
#             text='Тестовый текст',
#         )

#     # Проверим, что объект действительно было создан.
#     def test_successful_creation(self):
#         # При помощи обычного ORM-метода посчитаем количество записей в базе.
#         news_count = News.objects.count()
#         # Сравним полученное число с единицей.
#         self.assertEqual(news_count, 1) 


# class TestNews(TestCase):
#     # Все нужные переменные сохраняем в атрибуты класса.
#     TITLE = 'Заголовок новости'
#     TEXT = 'Тестовый текст'
    
#     @classmethod
#     def setUpTestData(cls):
#         cls.news = News.objects.create(
#             # При создании объекта обращаемся к константам класса через cls.
#             title=cls.TITLE,
#             text=cls.TEXT,
#         )

#     def test_successful_creation(self):
#         news_count = News.objects.count()
#         self.assertEqual(news_count, 1)

#     def test_title(self):
#         # Чтобы проверить равенство с константой -
#         # обращаемся к ней через self, а не через cls:
#         self.assertEqual(self.news.title, self.TITLE)


# class TestNews(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         # Создаём пользователя.
#         cls.user = User.objects.create(username='testUser')
#         # Создаём объект клиента.
#         cls.user_client = Client()
#         # "Логинимся" в клиенте при помощи метода force_login().        
#         cls.user_client.force_login(cls.user)
#         # Теперь через этот клиент можно отправлять запросы
#         # от имени пользователя с логином "testUser".

    


# ТЕСТИРОВАНИЕ МАРШРУТОВ 
# from http import HTTPStatus
# from django.test import TestCase
# from django.urls import reverse
# from django.contrib.auth import get_user_model
# from news.models import Comment, News


# User = get_user_model()


# class TestRoutes(TestCase):

#     def test_home_page(self):
#         # Вызываем метод get для клиента (self.client)
#         # и загружаем главную страницу.
#         response = self.client.get('/')
#         # Проверяем, что код ответа равен 200.
#         self.assertEqual(response.status_code, 200)


# class TestRoutes(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         '''Фикстура для создания новости.'''

#         cls.news = News.objects.create(title='Заголовок', text='Текст')
    
#     def test_home_page(self):
#         '''Главная страница доступна анонимному пользователю.'''

#         url = reverse('news:home')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, HTTPStatus.OK)

#     def test_detail_page(self):
#         '''Отдельная публикация доступна пользователю.'''

#         url = reverse('news:detail', args=(self.news.id,))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, HTTPStatus.OK)


# class TestRoutes(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         '''Фикстура для создания новости.'''

#         cls.news = News.objects.create(title='Заголовок', text='Текст')

#     def test_pages_availability(self):
#         '''Тестирование доступности страниц.'''
#         # Создаём набор тестовых данных - кортеж кортежей.
#         # Каждый вложенный кортеж содержит два элемента:
#         # имя пути и позиционные аргументы для функции reverse().
#         urls = (
#             # Путь для главной страницы не принимает
#             # никаких позиционных аргументов, 
#             # поэтому вторым параметром ставим None.
#             ('news:home', None),
#             # Путь для страницы новости 
#             # принимает в качестве позиционного аргумента
#             # id записи; передаём его в кортеже.
#             ('news:detail', (self.news.id,))
#         )
#         # Итерируемся по внешнему кортежу 
#         # и распаковываем содержимое вложенных кортежей:
#         for name, args in urls:
#             with self.subTest():
#                 # Передаём имя и позиционный аргумент в reverse()
#                 # и получаем адрес страницы для GET-запроса:
#                 url = reverse(name, args=args)
#                 response = self.client.get(url)
#                 self.assertEqual(response.status_code, HTTPStatus.OK) 

#ВАЖНО! ИСПОТЛЬЗОВАТЬ ЕГО МБ
# class TestRoutes(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         cls.news = News.objects.create(title='Заголовок', text='Текст')

#     def test_pages_availability(self):
#         '''Тестирование доступа отдельных страниц. '''

#         urls = (
#             ('news:home', None),
#             ('news:detail', (self.news.id,)),
#             ('users:login', None),
#             ('users:logout', None),
#             ('users:signup', None),
#         )
#         for name, args in urls:
#             with self.subTest(name=name):
#                 url = reverse(name, args=args)
#                 response = self.client.get(url)
#                 self.assertEqual(response.status_code, HTTPStatus.OK)