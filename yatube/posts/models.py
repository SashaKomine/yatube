from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    def __str__(self):
        return self.title

    title = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        verbose_name='Группа')
    slug = models.SlugField(
        unique=True,
        max_length=50,
        blank=False,
        null=False)
    description = models.TextField(
        blank=True,
        null=True)


class Post(models.Model):

    text = models.TextField(blank=False,
                            null=False,
                            verbose_name='Текст',
                            help_text='Обязательное поле')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата создания поста',
                                    db_index=True,
                                    help_text=('Добавляется'
                                               'автоматически '
                                               'при опубликовании'))
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        blank=False,
        null=False,
        verbose_name='Автор поста',
        help_text='Добавляется автоматически при опубликовании поста')
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа, к которой относится пост',
        help_text='Выберите группу для Вашего поста, это по Вашему желанию')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:15]

    class Meta():
        ordering = ('-pub_date', )


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='Комментарий',
        help_text='Комментарий к посту'
    )
    author = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='Автор комментария',
        help_text='Автор оставленного комментария'
    )
    text = models.TextField(blank=False,
                            null=False,
                            verbose_name='Текст',
                            help_text='Обязательное поле')

    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата создания комментария',
                                   help_text=('Добавляется'
                                              'автоматически '
                                              'при опубликовании'))


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='following'
    )
