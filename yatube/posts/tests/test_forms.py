from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

from posts.models import Post, Group, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug-group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        profile_url = reverse('posts:profile', args=[self.post.author])
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, profile_url)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=self.user
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма изменяет созданную запись."""
        post_detail_url = reverse('posts:post_detail', args=[self.post.id])
        editing_group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug1',
            description='Тестовое описание 1',
        )
        group_list_url = reverse('posts:group_list', args=[self.group.slug])
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': editing_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True,
        )
        response_group = self.authorized_client.get(group_list_url)
        self.assertNotIn(
            self.post,
            response_group.context['page_obj']
        )
        self.assertRedirects(response, post_detail_url)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=self.user,
            ).exists()
        )
