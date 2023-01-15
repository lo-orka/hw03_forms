from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group, User


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=PostURLTest.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.user = User.objects.create_user(username='noName')
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTest.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_status_is_correct_to_everyone(self):
        """URL-адрес доступен корректно для всех"""
        address_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }
        for address in address_url_names:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_error_page_status_404(self):
        """URL-адрес недоступен для несуществующих страниц"""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_url_redirect_anonymous_on_login(self):
        """Страница /create/ перенаправляет анонимного
        пользователя на страницу логина"""
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/'))

    def test_edit_url_redirect_not_author_on_(self):
        """Страница /edit/ перенаправляет не автора поста
        на страницу этого поста."""
        response = self.authorized_client_not_author.get(
            f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(
            response, (f'/posts/{self.post.id}/'))
