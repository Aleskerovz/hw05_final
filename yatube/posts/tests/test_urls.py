from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.user2 = User.objects.create_user(username='not_author')
        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_url_for_all_clients(self):
        """Страница / доступна любому пользователю."""
        url_names = [
            '/',
            '/group/test-slug/',
            '/profile/auth/',
            '/posts/1/'
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_for_auth_clients(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_for_guest_clients(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/',
            status_code=HTTPStatus.FOUND)

    def test_post_edit_url_for_author_client(self):
        """Страница /posts/<post_id>/edit/ доступна автору."""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_error_unexisting_page(self):
        """Несуществующая страница."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': '/posts/1/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_authorized_client_urls_uses_correct_template(self):
        """URL-адрес авторизованного пользователя
        использует соответствующий шаблон."""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/post_create.html')

    def test_author_client_urls_uses_correct_template(self):
        """URL-адрес для автора использует соответствующий шаблон."""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertTemplateUsed(response, 'posts/post_create.html')

    def test_post_edit_url_access_for_non_author_client(self):
        """Страница /posts/<post_id>/edit/
        недоступна авторизованному не автору."""
        response = self.authorized_client2.get('/posts/1/edit/')
        self.assertRedirects(
            response, '/posts/1/', status_code=HTTPStatus.FOUND)

    def test_follow_page_available_for_authenticated_user(self):
        """Страница /follow/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_page_unavailable_for_guest_user(self):
        """Страница /follow// недоступна гостю."""
        response = self.guest_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, '/auth/login/?next=/follow/')

    def test_follow_page_uses_correct_template(self):
        """URL-адрес /follow/ для авторизованного пользователя
        использует соответствующий шаблон."""
        response = self.authorized_client.get('/follow/')
        self.assertTemplateUsed(response, 'posts/follow.html')
