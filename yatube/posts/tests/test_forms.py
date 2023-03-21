from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post


class PostsTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='auth')
        self.another_user = get_user_model().objects.create_user(
            username='another_auth')
        self.group = Group.objects.create(
            title='Test Group',
            slug='test-group',
            description='Test description')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_auth = Client()
        self.another_auth.force_login(self.another_user)

    def create_post(self, text, group=None):
        return Post.objects.create(
            text=text,
            author=self.user,
            group=group or self.group)

    def test_create_post(self):
        """Валидная форма создает запись в базе данных."""
        initial_post_count = Post.objects.count()
        response = self.authorized_client.post(reverse('posts:post_create'), {
            'text': 'Test post',
            'group': self.group.pk})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), initial_post_count + 1)
        post = Post.objects.first()
        self.assertEqual(post.text, 'Test post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)

    def test_edit_post(self):
        """Валидная форма изменяет post_id в базе данных."""
        post = self.create_post('Original text')
        original_pub_date = post.pub_date
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[post.pk]), {
                'text': 'New text',
                'group': self.group.pk})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        post.refresh_from_db()
        self.assertEqual(post.text, 'New text')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.pub_date, original_pub_date)

    def test_edit_post_by_unauthorized_user(self):
        """Неавторизованный пользователь не может редактировать пост."""
        post = self.create_post('Original text')
        original_post = post
        response = self.guest_client.post(
            reverse('posts:post_edit', args=[post.pk]), {
                'text': 'New text',
                'group': self.group.pk})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        post.refresh_from_db()
        self.assertEqual(post.text, original_post.text)
        self.assertEqual(post.group, original_post.group)
        self.assertEqual(post.pub_date, original_post.pub_date)
        self.assertEqual(post.author, original_post.author)

    def test_create_post_by_unauthorized_user(self):
        """Неавторизованный пользователь не может создать новый пост."""
        initial_post_count = Post.objects.count()
        response = self.guest_client.post(reverse('posts:post_create'), {
            'text': 'Test post',
            'group': self.group.pk})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), initial_post_count)

    def test_edit_post_by_another_user(self):
        """Авторизованный пользователь не может изменять чужой пост."""
        post = self.create_post('Original text')
        original_post = post
        response = self.another_auth.post(
            reverse('posts:post_edit', args=[post.pk]), {
                'text': 'New text',
                'group': self.group.pk})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        post.refresh_from_db()
        self.assertEqual(post.text, original_post.text)
        self.assertEqual(post.group, original_post.group)
        self.assertEqual(post.pub_date, original_post.pub_date)
        self.assertEqual(post.author, original_post.author)

    def test_create_post_without_group(self):
        """Пост создается без указания группы"""
        initial_post_count = Post.objects.count()
        response = self.authorized_client.post(reverse('posts:post_create'), {
            'text': 'Test post without group'})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), initial_post_count + 1)
        post = Post.objects.first()
        self.assertEqual(post.text, 'Test post without group')
        self.assertEqual(post.author, self.user)
        self.assertIsNone(post.group)
