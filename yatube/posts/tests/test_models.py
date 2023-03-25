from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Follow, Group, Post

User = get_user_model()

NUM_CHARACTERS = 15


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test title',
            slug='test-slug',
            description='Test description'
        )

    def test_group_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Заголовок',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_title_max_length(self):
        """Максимальная длина поля 'title' равна 200 символам."""
        group = GroupModelTest.group
        max_length = group._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-group',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Text test for 15 characters',
        )

    def test_post_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_meta_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        self.assertEqual(Post._meta.verbose_name, 'Публикацию')

    def test_meta_verbose_name_plural(self):
        """verbose_name_plural в полях совпадает с ожидаемым."""
        self.assertEqual(Post._meta.verbose_name_plural, 'Публикации')

    def test_post_str(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:NUM_CHARACTERS]
        self.assertEqual(expected_object_name, str(post))


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-group',
            description='Test description')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Text test for 15 characters',
            group=cls.group)
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Test comment')

    def test_comment_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Публикация',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата публикации',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_comment_text_help_text(self):
        """help_text в поле 'text' совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        expected_help_text = 'Введите ваш комментарий'
        self.assertEqual(
            comment._meta.get_field('text').help_text, expected_help_text)

    def test_comment_str(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        comment = CommentModelTest.comment
        expected_object_name = comment.text[:NUM_CHARACTERS]
        self.assertEqual(expected_object_name, str(comment))

    def test_comment_ordering(self):
        """Комментарии отсортированы по
        дате публикации (created) по убыванию."""
        expected_ordering = ('-created',)
        self.assertEqual(Comment._meta.ordering, expected_ordering)


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.another_user = User.objects.create_user(username='anotheruser')

    def test_follow_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        follow = Follow(
            user=FollowModelTest.user, author=FollowModelTest.another_user)
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    follow._meta.get_field(value).verbose_name, expected)

    def test_follow_str(self):
        """Проверяем, что у модели Follow корректно работает __str__."""
        follow = Follow(
            user=FollowModelTest.user, author=FollowModelTest.another_user)
        expected_object_name = (
            f'{FollowModelTest.user.username} подписан на '
            f'{FollowModelTest.another_user.username}')
        self.assertEqual(expected_object_name, str(follow))
