import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse, reverse_lazy
from posts.forms import CommentForm, PostForm

from ..models import Comment, Follow, Group, Post

User = get_user_model()

NUM_OF_POSTS = 15
NUM_OF_POSTS_2PAGE = 5
EXPENDED_NUM_OF_POSTS = 10


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test title',
            slug='test-slug',
            description='Test description'
        )
        cls.user = User.objects.create_user(username='auth')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group)
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Test comment')
        cls.templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
            reverse('posts:group_list', args=[cls.group.slug]),
            'posts/post_detail.html':
            reverse('posts:post_detail', args=[cls.post.pk]),
            'posts/profile.html':
            reverse('posts:profile', args=[cls.user.username]),
        }

    @classmethod
    def tearDownClass(cls):
        """Удаляем временную папку для медиа-файлов."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower = User.objects.create_user(username='leo')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.follower)
        self.not_follower = User.objects.create_user(username='mark')
        self.authorized_client3 = Client()
        self.authorized_client3.force_login(self.not_follower)
        self.author = User.objects.create_user(username='testauthor')

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create(self):
        """При открытии страницы создания поста используется
        форма PostForm."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)
        form_fields = {
            'text': forms.CharField,
            'group': forms.ModelChoiceField,
            'image': forms.ImageField,
        }
        for field, expected_type in form_fields.items():
            self.assertIsInstance(
                response.context['form'].fields[field], expected_type)
        self.assertNotIn('is_edit', response.context)

    def test_post_edit(self):
        """При открытии страницы редактирования поста используется
        форма PostForm."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[self.post.pk]))
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField,
            'image': forms.ImageField,
        }
        for field, expected_type in form_fields.items():
            self.assertIsInstance(
                response.context['form'].fields[field], expected_type)
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertTrue(response.context['is_edit'])

    def test_index_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.context['page_obj'].paginator.count, 1)
        self.assertIn(self.post, response.context['page_obj'])
        self.assertEqual(
            response.context['page_obj'][0].image, self.post.image)

    def test_group_posts_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.context['page_obj'].paginator.count, 1)
        self.assertEqual(response.context['group'], self.group)
        self.assertIn(self.post, response.context['page_obj'])
        self.assertEqual(
            response.context['page_obj'][0].image, self.post.image)

    def test_profile_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.context['page_obj'].paginator.count, 1)
        self.assertEqual(response.context['author'], self.user)
        self.assertIn(self.post, response.context['page_obj'])
        self.assertEqual(
            response.context['page_obj'][0].image, self.post.image)

    def test_post_detail_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['post'].image, self.post.image)
        self.assertIsInstance(response.context['form'], CommentForm)
        self.assertEqual(response.context['post'].comments.count(), 1)
        self.assertEqual(
            response.context['post'].comments.first().text, 'Test comment')

    def test_post_appears_on_homepage(self):
        """Проверяет, что созданный пост появляется на главной странице."""
        response = self.client.get(reverse('posts:index'))
        self.assertIn(self.post, response.context['page_obj'])

    def test_post_appears_on_group_page(self):
        """Проверяет, что созданный пост появляется
        на странице выбранной группы."""
        response = self.client.get(
            reverse('posts:group_list', args=[self.group.slug]))
        self.assertIn(self.post, response.context['page_obj'])

    def test_post_appears_on_user_profile(self):
        """Проверяет, что созданный пост появляется в профиле пользователя."""
        response = self.client.get(
            reverse('posts:profile', args=[self.user.username]))
        self.assertIn(self.post, response.context['page_obj'])

    def test_post_not_in_unrelated_group(self):
        """Проверяет, что созданный пост не появляется
        в группе, для которой он не был предназначен."""
        unrelated_group = Group.objects.create(
            title='Unrelated Group',
            slug='unrelated-group',
            description='Unrelated group description')
        response = self.client.get(
            reverse('posts:group_list', args=[unrelated_group.slug]))
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_comment_auth(self):
        """Проверяет, что комментировать посты может
        только авторизованный пользователь."""
        url = reverse('posts:post_detail', args=[self.post.id])
        response = self.client.get(url)
        self.assertNotContains(response, 'form')
        response = self.authorized_client.get(url)
        self.assertContains(response, 'form')

    def test_cache_index(self):
        """Проверяет работу кеша на главной странице."""
        url = reverse('posts:index')
        response1 = self.client.get(url)
        content1 = response1.content
        Post.objects.create(
            author=self.user, text='Test post')
        response2 = self.client.get(url)
        content2 = response2.content
        self.assertEqual(content1, content2)
        cache.clear()
        response3 = self.client.get(url)
        content3 = response3.content
        self.assertNotEqual(content2, content3)

    def test_follow(self):
        """Проверяет, что авторизованный пользователь может подписываться на
        других пользователей"""
        response = self.authorized_client.get(
            reverse('posts:profile_follow', args=[self.follower.username]))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(
            Follow.objects.filter(
                author=self.follower, user=self.user).exists())

    def test_unfollow(self):
        """Проверяет, что авторизованный пользователь может отписываться от
        других пользователей."""
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow', args=[self.follower.username]))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(
            Follow.objects.filter(
                author=self.follower, user=self.user).exists())

    def test_follow_index(self):
        """Проверяет, что Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        Follow.objects.create(author=self.user, user=self.follower)
        response = self.authorized_client2.get(reverse('posts:follow_index'))
        self.assertContains(response, self.post.text)
        response = self.authorized_client3.get(reverse('posts:follow_index'))
        self.assertNotContains(response, self.post.text)


class PaginatorTestCase(TestCase):
    def setUp(cls):
        cls.user = User.objects.create_user(username='auth')
        cls.follower = User.objects.create_user(username='testfollower')
        cls.group = Group.objects.create(
            title='Test title',
            slug='test-slug',
            description='Test description'
        )
        posts = [Post(
            text=f'Test post {i}',
            author=cls.user,
            group=cls.group,
        ) for i in range(NUM_OF_POSTS)]
        Post.objects.bulk_create(posts)
        cls.pages = {
            'index': reverse_lazy('posts:index'),
            'group_list': reverse_lazy('posts:group_list',
                                       kwargs={'slug': cls.group.slug}),
            'profile': reverse_lazy('posts:profile',
                                    kwargs={'username': cls.user.username})}

    def test_paginator_on_index_page(self):
        """Количество постов на главной странице равно 10."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(
            response.context['page_obj'].object_list), EXPENDED_NUM_OF_POSTS)
        self.assertTrue(response.context['page_obj'].has_next())

    def test_paginator_on_group_posts_page(self):
        """Количество постов на странице с группами равно 10."""
        response = self.client.get(
            reverse('posts:group_list', args=('test-slug',)))
        self.assertEqual(len(
            response.context['page_obj'].object_list), EXPENDED_NUM_OF_POSTS)
        self.assertTrue(response.context['page_obj'].has_next())

    def test_paginator_on_profile_page(self):
        """Количество постов на странице автора равно 10."""
        response = self.client.get(
            reverse('posts:profile', args=('auth',)))
        self.assertEqual(len(
            response.context['page_obj'].object_list), EXPENDED_NUM_OF_POSTS)
        self.assertTrue(response.context['page_obj'].has_next())

    def test_second_page_contains_five_records(self):
        """Количество постов на второй странице должно быть 5."""
        for page_name, page_url in self.pages.items():
            with self.subTest(page=page_name):
                response = self.client.get(str(page_url) + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']), NUM_OF_POSTS_2PAGE)

    def test_paginator_on_follow_page(self):
        """Количество постов на странице подписок равно 10."""
        Follow.objects.create(author=self.user, user=self.follower)
        self.client.force_login(self.follower)
        response = self.client.get(reverse('posts:follow_index'))
        self.assertEqual(len(
            response.context['page_obj'].object_list), EXPENDED_NUM_OF_POSTS)
        self.assertTrue(response.context['page_obj'].has_next())

    def test_paginator_ofvn_follow_page(self):
        """Количество постов на второй странице подписок должно быть 5."""
        Follow.objects.create(author=self.user, user=self.follower)
        self.client.force_login(self.follower)
        response = self.client.get(reverse('posts:follow_index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']), NUM_OF_POSTS_2PAGE)
