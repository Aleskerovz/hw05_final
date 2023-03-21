from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

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
