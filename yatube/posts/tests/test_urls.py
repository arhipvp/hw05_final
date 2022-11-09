from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from django.core.cache import cache

User = get_user_model()


class UrlAndTemplateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.testuser = User.objects.create_user(username='TestUser')
        cls.testuser2 = User.objects.create_user(username='TestUser2')

        cls.testgoup = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug',
        )
        cls.test_post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.testuser,
            group=cls.testgoup,
        )
        cls.TEMPLATES_FOR_URL = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': cls.testuser.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': cls.test_post.pk}
            ),
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.testuser)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.testuser2)
        self.guest_client = Client()
        cache.clear()

    def test_HTTPStatus_and_Template_URL_public(self):
        """Проверяем доступность и соответствие шаблонов к URL """
        for template, address in self.TEMPLATES_FOR_URL.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertAlmostEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_redirect_from_privat(self):
        """"
        Проверяем редирект при редактировании
            чужих постов (пользователь авторизован)
        """
        Redirect_url = {
            reverse(
                'posts:post_edit', kwargs={'post_id': self.test_post.pk}
            ): reverse(
                'posts:post_detail', kwargs={'post_id': self.test_post.pk}
            )
        }
        for address, readress in Redirect_url.items():
            response = self.authorized_client2.get(address)
            self.assertRedirects(response, readress)

    def test_edit_own_post(self):
        "Проверяем доступность своих страниц"
        CHECH_OWN_URL = {
            reverse(
                'posts:post_edit', kwargs={'post_id': self.test_post.pk}
            )
        }
        for address in CHECH_OWN_URL:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_editpost_guest(self):
        """"
        Проверяем редирект при редактировании
            чужих постов (пользователь неавторизован)
        """
        Redirect_url = {
            reverse(
                'posts:post_edit', kwargs={'post_id': self.test_post.pk}
            ): reverse('users:login')
        }
        for adress, readress in Redirect_url.items():
            response = self.guest_client.get(adress)
            self.assertIn(readress, response['location'])
