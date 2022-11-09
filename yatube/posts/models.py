from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Group title",
        help_text="Название группы",
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Slug",
        help_text="Слаг Группы",
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Описание группы",
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Text Post",
        help_text="Текст поста",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="publication of date",
        help_text="Дата публикации",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Author",
        help_text="Автор",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Группа поста",
        related_name="posts",
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField(
        verbose_name="Text comment",
        help_text="Текст комментария",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Author",
        help_text="Автор",
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="publication of date",
        help_text="Дата публикации",
    )

    class Meta:
        ordering = ["-created"]

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='user_author_pair_unique',
                fields=['user', 'author'],
            ),
        ]
