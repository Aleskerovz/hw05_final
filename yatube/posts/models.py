from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

NUM_CHARACTERS = 15


class Group(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Группу'
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField('Текст', help_text='Текст нового поста')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts')
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='posts')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Публикацию'
        verbose_name_plural = 'Публикации'

    def __str__(self) -> str:
        return self.text[:NUM_CHARACTERS]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Введите ваш комментарий'
    )
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:NUM_CHARACTERS]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписчика'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
