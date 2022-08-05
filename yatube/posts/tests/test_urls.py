from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import Post, Group

User = get_user_model()


class TestPostURL(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_group',
            description='test_description',
            slug='test_slug'
        )
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            text='test poooost',
            author=cls.user,
            group=cls.group)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = Client()
        self.author.force_login(TestPostURL.user)

    def test_for_guest_status(self):
        """Тестируем гостевые url Post"""
        template_urls = ('/',
                         f'/group/{self.group.slug}/',
                         f'/profile/{self.user.username}/',
                         f'/posts/{self.post.id}/')
        for address in template_urls:
            response = self.client.get(address)
            with self.subTest(address=address):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexs_URL(self):
        """Открытие несуществующей страницы"""
        response = self.client.get('/unexsisting_url/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_for_auth(self):
        """Страница создания поста пользователем открывается"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_for_author(self):
        """Страница редактирования для автора открывается"""
        response = self.author.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_for_guest(self):
        """Страница создания для гостя"""
        response = self.client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_for_guest(self):
        """Страница редактирования для гостя"""
        response = self.client.get(f'posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestTemplates(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_group',
            description='test_description',
            slug='test_slug'
        )
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            text='test poooost',
            author=cls.user,
            group=cls.group)

    def setUp(self):
        self.user1 = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = Client()
        self.author.force_login(TestTemplates.user)

    def test_for_guest(self):
        """Тестируем шаблоны гостевых url"""
        profile_temp = 'posts/profile.html'
        template_urls = {#'/': '/posts/index.html',
                         f'/group/{self.group.slug}/': 'posts/group_list.html',
                         f'/profile/{self.user.username}/': profile_temp,
                         f'/posts/{self.post.id}/': 'posts/post_detail.html'}
        for address, template in template_urls.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template, f'no {template} ')

    def test_create_post_for_auth(self):
        """Шаблон создания поста пользователем открывается"""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_for_author_in_edit(self):
        """Шаблон редактирования для автора открывается"""
        response = (self.author.get(f'/posts/{self.post.id}/edit/'))
        self.assertTemplateUsed(response, 'posts/create_post.html')


class TestRedirect(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_group',
            description='test_description',
            slug='test_slug'
        )
        cls.user = User.objects.create_user(username='test_user')
        cls.user1 = User.objects.create_user(username='test_user1')
        cls.post = Post.objects.create(
            text='test poooost',
            author=cls.user,
            group=cls.group)

    def setUp(self):
        self.auth_user = Client()
        self.auth_user.force_login(self.user1)

    def test_create_edit_guest(self):
        """редирект гостей со страниц авторизированных пользователей"""
        edit_template = f'/auth/login/?next=/posts/{self.post.id}/edit/'
        templ_redirects = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit/': edit_template}
        for template, redirect in templ_redirects.items():
            with self.subTest(template=template):
                response = self.client.get(template, follow=True)
                self.assertRedirects(response, redirect)

    def test_create_edit_auth(self):
        """редирект пользователя со страницы редактирования автора """
        response = self.auth_user.get(
            f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(response, f'/posts/{self.post.id}/')
