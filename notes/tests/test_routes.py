from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тесты путей приложения Notes."""

    @classmethod
    def setUpTestData(cls):
        """Создание данных для тестирования."""

        cls.author = User.objects.create(username='johndoe')
        cls.nonauthor = User.objects.create(username='janedoe')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст',
            author=cls.author
        )
    
    def test_pages_availability(self):
        """Тест проверки доступности общих страниц."""

        urls = (
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
            ('notes:home', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                respounse = self.client.get(url)
                self.assertEqual(respounse.status_code, HTTPStatus.OK)

    def test_redirect_for_anon_client(self):
        """
        Тест редиректа анонима с запрещенных
        для анонимного просмотра страниц.
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:list', None),
            ('notes:detail', (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                respounse = self.client.get(url)
                self.assertRedirects(respounse, redirect_url)

    def test_availability_for_note_and_notelist_check_edit_and_delete(self):
        """
        Тест доступности страниц редактирования, удаления заметки,
        а также просмотра конкретной заметки и списка заметок
        только для автора.
        """

        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.nonauthor, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    respounse = self.client.get(url)
                    self.assertEqual(respounse.status_code, status)
