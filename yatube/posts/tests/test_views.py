from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from posts.models import Post, Group, User

PAGINATOR_POSTS = 10
PAGES_PAGINATOR = [1, 2]


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        Post.objects.bulk_create(
            [cls.post for _ in range(PAGINATOR_POSTS * len(
                PAGES_PAGINATOR))]
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsTest.user)

    def check_page_context(self, context, post=False):
        if post:
            self.assertIn('post', context)
            post = context['post']
        else:
            self.assertIn('page_obj', context)
            post = context['page_obj'][0]
        self.assertEqual(post.author, PostViewsTest.post.author)
        self.assertEqual(post.text, PostViewsTest.post.text)
        self.assertEqual(post.group.slug, PostViewsTest.group.slug)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{PAGINATOR_POSTS}/': 'posts/post_detail.html',
            f'/posts/{PAGINATOR_POSTS}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_page_context(response.context)

    def test_group_and_profile_show_correct_context(self):
        """group и profile сформирован с правильным контекстом."""
        responses = {
            'group': self.authorized_client.get(
                reverse('posts:group_list', args=[self.group.slug])),
            'author': self.authorized_client.get(
                reverse('posts:profile', args=[self.post.author])),
        }
        for field, response in responses.items():
            with self.subTest(field=field):
                count = response.context[field].posts.select_related(
                    'group', 'author').count()
                self.assertEqual(count, PAGINATOR_POSTS * len(
                    PAGES_PAGINATOR))

    def test_create_and_edit_show_correct_context(self):
        """create и edit сформирован с правильным контекстом."""
        responses_create_edit = [
            self.authorized_client.get(
                reverse('posts:post_create')),
            self.authorized_client.get(
                reverse('posts:post_edit', args=[PAGINATOR_POSTS]))
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for respons in responses_create_edit:
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = respons.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_post_detail_show_correct_context(self):
        """post_detail сформирован с правильным контекстом."""
        response_post_detail = self.authorized_client.get(
            reverse('posts:post_detail', args=[PAGINATOR_POSTS])
        )
        self.check_page_context(response_post_detail.context, post=True)

    def test_post_is_on_right_page(self):
        """"Пост отображается на верных старницах"""
        group1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug1',
            description='Тестовое описание 1',
        )
        urls = [
            reverse('posts:index'),
            reverse('posts:profile', args=[self.post.author]),
            reverse('posts:group_list', args=[self.group.slug]),
        ]
        for url in urls:
            response = self.authorized_client.get(url)
            self.check_page_context(response.context)

        response_group1 = self.authorized_client.get(
            reverse('posts:group_list', args=[group1.slug])
        )
        self.assertNotIn(
            self.post,
            response_group1.context['page_obj']
        )

    def test_page_paginator(self):
        """Тестируем пагинатор на первой и второй странице"""
        index_url = reverse('posts:index')
        profile_url = reverse('posts:profile', args=[self.post.author])
        group_list_url = reverse('posts:group_list', args=[self.group.slug])
        paginate_page = [
            index_url + '?page={}',
            group_list_url + '?page={}',
            profile_url + '?page={}',
        ]
        for count in PAGES_PAGINATOR:
            for page in paginate_page:
                response = self.authorized_client.get(page.format(count))
                self.assertEqual(
                    len(response.context['page_obj']),
                    PAGINATOR_POSTS
                )
