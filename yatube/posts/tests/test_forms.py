from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, Comment

User = get_user_model()
FORM_FIELD_COUNT = 3


class TestPostCreateForm(TestCase):
    """Форма для создания поста."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test user 1')
        cls.group = Group.objects.create(
            title='test group 1',
            slug='test_slug1'
        )
        cls.post = Post.objects.create(
            text='text1',
            author=cls.user,
            group=cls.group
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )

        cls.uploaded_pic = SimpleUploadedFile(
            name='small_gif',
            content=small_gif,
            content_type='image/gif'
        )

    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.auth_user = Client()
        self.auth_user.force_login(self.user)

    def test_form_create(self):
        """Пользователь создал пост с картинкой"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'test text1',
            'group': self.group.id,
            'image': self.uploaded_pic}
        self.auth_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author.username, self.user.username)
        self.assertEqual(post.image, self.post.image)

    def test_guest_post(self):
        """ Пост при отсутсвии авторизации """
        post_count = Post.objects.count()
        form_data = {
            'text': 'text guest',
            'group': self.group.id}
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,)
        self.assertEqual(post_count, Post.objects.count())

    def test_post_edit_form(self):
        """форма редактирования работает"""
        form_data = {'text': 'text post'}
        self.auth_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        form_data = {
            'text': 'text edit',
            'group': self.group.id
        }
        post_count = Post.objects.count()
        self.auth_user.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(post_count, Post.objects.count())


class TestCommentPost(TestCase):
    """Тестированеи формы комментария"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test user 1')
        cls.user1 = User.objects.create(username='text user 2')
        cls.group = Group.objects.create(
            title='test group 1',
            slug='test_slug1'
        )
        cls.post = Post.objects.create(
            text='text1',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.auth_user = Client()
        self.auth_user.force_login(self.user1)

    def test_comment_auth_user(self):
        """комментарий от пользователя создался"""
        form_data = {'text': 'comment1'}
        self.auth_user.post(reverse('posts:add_comment',
                            kwargs={'post_id': self.post.id}),
                            data=form_data,
                            follow=True)
        comment = Comment.objects.last()
        self.assertEqual(comment.text, Comment.objects.last().text)

    def test_comment_guest(self):
        """комментарий от гостя не создался"""
        count_post = Comment.objects.count()
        form_data = {'text': 'comment1'}
        self.client.post(reverse('posts:add_comment',
                                 kwargs={'post_id': self.post.id}),
                         data=form_data,
                         follow=True)
        self.assertEqual(count_post, Comment.objects.count())
