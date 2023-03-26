import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_auth = Client()
        self.another_auth.force_login(self.another_user)

    @classmethod
    def tearDownClass(cls):
        """Удаляем временную папку для медиа-файлов."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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

    def test_comment_post(self):
        """Проверяет, что после успешной отправки
        комментарий появляется на странице поста."""
        comment_text = 'Test comment'
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            {'text': comment_text})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        comments_count = Comment.objects.count()
        self.assertEqual(comments_count, 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.text, comment_text)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)

    def test_guest_cannot_comment_post(self):
        """Проверяет, что гость не может создать комментарий."""
        comment_text = 'Test comment'
        response = self.guest_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            {'text': comment_text})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        comments_count = Comment.objects.count()
        self.assertEqual(comments_count, 0)

    def test_create_post_with_image_and_redirect(self):
        """Валидная форма создает запись с изображением в базе данных
        и пользователь будет перенаправлен на свой профиль."""
        initial_post_count = Post.objects.count()
        form_data = {
            'text': 'Test post with image',
            'group': self.group.pk,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), initial_post_count + 1)
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.image.read(), self.small_gif)
        self.assertRedirects(
            response, reverse('posts:profile', args=[self.user.username]))
