from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=PostModelTest.user,
            text='Тестовый пост',
            group=cls.group,
            pub_date='Дата',

        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='noName')
        self.authorized_client = Client()
        self.authorized_client.force_login(PostModelTest.user)
    
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', args={self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', args={self.user.username}): 'posts/profile.html',
            reverse('posts:post_detail', args={self.post.id}):   'posts/post_detail.html',
            reverse('posts:post_edit', args={self.post.id}):  'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        context_first_post = response.context['page_obj'][0]
        self.assertEqual(context_first_post, self.post)

    def test_group_and_profile_show_correct_context(self):
        """group и profile сформирован с правильным контекстом."""
        response_group_and_profile = {
            'group': self.authorized_client.get(
                reverse('posts:group_list', args=[self.group.slug])),
            'author': self.authorized_client.get(
                reverse('posts:profile', args=[self.user.username])),
        }
        form_fields = {
            'group': forms.fields.ChoiceField,
            'author': forms.fields.ChoiceField,
        }
        for values, response in response_group_and_profile.items():
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    count = values.context[fields].post.select_related(
                        'group', 'author').count()
                    self.assertIsInstance(count, expected)

    def test_create_and_edit_show_correct_context(self):
        """create и edit сформирован с правильным контекстом."""
        responses_create_edit = [
            self.authorized_client.get(
                reverse('posts:post_create')),
            self.authorized_client.get(
                reverse('posts:post_edit', args=[self.post.id]))
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
            reverse('posts:post_detail', args=[self.post.id])
        )
        post_detail_context = response_post_detail.context['post']
        self.assertEqual(post_detail_context, self.post)