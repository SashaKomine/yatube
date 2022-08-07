from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files import File
from django.core.cache import cache
from django.conf import settings

from posts.forms import PostForm
from posts.models import Post, Group, Follow


User = get_user_model()


class TestNameNamespace(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='LeonidYacubovic')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug'
        )
        cls.post = Post.objects.create(
            text='test_text',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.author_auth = Client()
        self.author_auth.force_login(self.user)
        cache.clear()

    def test_name_and_namespace(self):
        """ во view-функциях используются
        правильные html-шаблоны. """
        post_detail = 'posts/post_detail.html'
        create_post = 'posts/create_post.html'

        templates_name_and_namespace = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user.username}):
            'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): post_detail,
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}): create_post,
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for func, template in templates_name_and_namespace.items():
            with self.subTest(template=template):
                response = self.author_auth.get(func)
                self.assertTemplateUsed(response, template)


class TestPagination(TestCase):
    """ посты выводятся постранично по 10 штук """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='LeonidYacubovic')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug'
        )

        Post.objects.bulk_create(
            [(Post(author=cls.user,
                   group=cls.group,
                   text=f'test post {i}')
              )for i in range(14)])

    def setUp(self):
        self.auth_user = Client()
        self.auth_user.force_login(self.user)
        cache.clear()

    def test_1_page(self):
        """1-я страница пагинации"""
        pagi_dict = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': self.group.slug}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={
                                              'username': self.user.username})}
        for template, rev in pagi_dict.items():
            response = self.auth_user.get(rev)
            with self.subTest(template=template):
                self.assertEqual(
                    len(response.context['page_obj']
                        .paginator.page(1)), settings.COUNT_POST)

    def test_2_page(self):
        """2-я страница пагинации"""
        second_page = 4
        pagi_dict = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': self.group.slug}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={
                                              'username': self.user.username})}
        for template, rev in pagi_dict.items():
            response = self.auth_user.get(rev)
            with self.subTest(template=template):
                self.assertEqual(
                    len(response.context['page_obj']
                        .paginator.page(2)), second_page)


class TestContext(TestCase):
    """Тестирование наполнения страниц"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='LeonidYacubovic')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='test post 1',
            image=File('1.png'))

    def setUp(self):
        self.auth_user = Client()
        self.auth_user.force_login(self.user)
        cache.clear()

    def sample_context(self, obj):
        self.assertEqual(obj.text, self.post.text)
        self.assertEqual(obj.author.username, self.user.username)
        self.assertEqual(obj.group.title, self.group.title)
        self.assertEqual(obj.id, self.post.id)

    def test_context_group(self):
        """Контекст группы соответсвует"""
        response = self.auth_user.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_obj = response.context['page_obj'][0]
        self.sample_context(first_obj)
        self.assertEqual(first_obj.group, self.group)

    def test_post_in_group(self):
        """Пост в группе """
        response = self.auth_user.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_obj = response.context['page_obj'][0]
        self.assertEqual(first_obj.text, self.post.text)

    def test_group_in_profile(self):
        """Отображение группы в профайле"""
        response = self.auth_user.get(
            reverse('posts:profile', kwargs={'username': TestContext.user
                                             .username}))
        first_obj = response.context['page_obj'][0]
        self.assertEqual(first_obj.group.title, self.group.title)

    def test_profile_context(self):
        """ Контекст профайла совпадает """
        response = self.auth_user.get(
            reverse('posts:profile', kwargs={'username': TestContext.user
                                             .username}))
        first_obj = response.context['page_obj'][0]
        self.sample_context(first_obj)

    def test_post_detail(self):
        """Детализация поста проходит"""
        response = self.auth_user.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        first_obj = response.context['post']
        self.sample_context(first_obj)

    def test_post_create(self):
        """При создании поста открывается нужная форма"""
        response = self.auth_user.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_edit(self):
        """Post edit открыает форму и выводит контекст"""
        response = self.auth_user.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context['is_edit'], True)
        self.assertIsInstance(response.context['is_edit'], bool)
        self.assertIsInstance(response.context['post'], Post)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_non_else_group(self):
        """ Пост не попал в другую группу """
        group2 = Group.objects.create(
            title='group2',
            slug='group2-slug')
        response = self.auth_user.get(
            reverse('posts:group_list', kwargs={'slug': group2.slug}))
        self.assertTrue(response.context['group'].title, self.post.group)

    def test_post_non_else_author(self):
        """Пост не попал к другому автору"""
        author2 = User.objects.create(username='author2')
        response = self.auth_user.get(
            reverse('posts:profile', kwargs={'username': TestContext.user
                                             .username}))
        first_obj = response.context['page_obj'][0]
        self.assertNotEqual(first_obj.author, author2.username)

    def test_image(self):
        """Изображения в контексте"""
        rev = (
            reverse('posts:profile', kwargs={'username': self.user.username}),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:index'))
        for key in rev:
            with self.subTest(key=key):
                response = self.auth_user.get(key)
                self.assertIsNotNone(
                    response.context['page_obj'][0].image)

    def test_image_in_post_detail(self):
        """Изображение в деталях поста"""
        response = self.auth_user.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertIsNotNone(response.context['post'].image)


class TestCache(TestCase):
    """Тестирование кеша"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='LeonidYacubovic')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='test post 1',
            image=File('1.png'))

    def setUp(self):
        cache.clear()

    def test_index_cache(self):
        """Кеш сохраняется и через 20 секунд удаляется"""
        response = self.client.get(reverse('posts:index'))
        post1 = Post.objects.last()
        post1.delete()
        self.assertEqual(
            response.context['page_obj'][0].text, post1.text)
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotEqual(Post.objects.filter(
            text=post1.text), self.post.text)


class TestFollow(TestCase):
    """Тестирование подписок"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='LeonidYacubovic')
        cls.user1 = User.objects.create(username='LeonidYacubovic1')
        cls.user2 = User.objects.create(username='test3')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='test post 1',
            image=File('1.png'))

    def setUp(self):
        self.auth_user = Client()
        self.auth_user.force_login(self.user1)
        self.author = Client()
        self.author.force_login(self.user)
        cache.clear()

    def test_following(self):
        """Авторизованный пользователь может подписываться на других
        пользователей """
        self.auth_user.get(
            reverse('posts:profile_follow', args=[self.user.username]))
        self.assertIsNotNone(Follow.objects.filter(
            author=self.user, user=self.user1))

    def test_self_following(self):
        """Подписка на самого себя"""
        self.author.get(
            reverse('posts:profile_follow', args=[self.user.username]))
        self.assertFalse(Follow.objects.filter(user=self.user,
                                               author=self.user).exists())

    def test_unfollowing(self):
        """Авторизованный пользователь может удалять из подписок."""
        Follow.objects.create(user=self.user1, author=self.user)
        self.auth_user.get(
            reverse('posts:profile_unfollow', args=[self.user.username]))
        self.assertFalse(Follow.objects.filter(
            author=self.user, user=self.user1).exists())

    def test_follow_list(self):
        """Новая запись пользователя появляется в ленте тех,
         кто на него подписан и не появляется в ленте тех, кто не подписан."""
        Follow.objects.create(user=self.user1, author=self.user)
        response = self.auth_user.get(reverse('posts:follow_index'))
        first_obj = response.context['page_obj'][0]
        self.assertEqual(first_obj.author, self.user)
