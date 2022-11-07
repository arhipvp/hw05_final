from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

COUNT_POST_IN_PAGE = 10

def generate_test_posts(count: int, author: User, group: Group):
    postlist = []
    for i in range(count):
        post = Post(
            text=(f'Тестовый текст №{i}'),
            group=group,
            author=author,
        )
        postlist.append(post)
    Post.objects.bulk_create(postlist)

class ViewTests(TestCase):



    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.testuser = User.objects.create_user(username="TestUser")

        cls.group1 = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug-1',
        )
        cls.group2 = Group.objects.create(
            title='Тестовый заголовок 2',
            description='Тестовый текст 2',
            slug='test-slug-2',
        )

        generate_test_posts(20, cls.testuser, cls.group1)
        generate_test_posts(20, cls.testuser, cls.group2)

        cls.post_with_group = Post.objects.create(
            text='тестовый пост c указанием группы 1',
            group=cls.group1,
            author=cls.testuser,
        )
        cls.test_post_user_last = Post.objects.first()

        cls.TEMPLATES_FOR_VIEWS_AUTH = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': cls.group1.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': cls.testuser.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': cls.test_post_user_last.pk
                }
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': cls.test_post_user_last.pk
                }
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        cls.TEMPLATES_FOR_VIEWS_GUEST = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': cls.group1.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': cls.testuser.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={
                    'post_id': cls.test_post_user_last.pk
                }
            ),
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.testuser)

    def test_templates_view_auth(self):
        """(авторизован)Во view-функциях используются правильные шаблоны."""
        for reverse_view, template in self.TEMPLATES_FOR_VIEWS_AUTH.items():
            with self.subTest(address=reverse_view):
                response = self.authorized_client.get(reverse_view)
                self.assertTemplateUsed(response, template)

    def test_templates_view_guest(self):
        """(неавторизован)Во view-функциях используются правильные шаблоны."""
        for template, reverse_view in self.TEMPLATES_FOR_VIEWS_GUEST.items():
            with self.subTest(address=reverse_view):
                response = self.guest_client.get(reverse_view)
                self.assertTemplateUsed(response, template)

    def test_post_create_index(self):
        """Если при создании поста указать группу, то появляется на главной"""

        response = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(response, self.post_with_group.text)

    def test_post_create_group(self):
        """Если при создании поста указать группу,
        то этот пост появляется на странице группы"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.post_with_group.group.slug}
            )
        )
        self.assertContains(response, self.post_with_group.text)

    def test_post_create_profile(self):
        """Если при создании поста указать группу,
        то этот пост появляется в профайле"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': self.testuser.username}
            )
        )
        self.assertContains(response, self.post_with_group.text)

    def test_post_create_no_other_group(self):
        """Пост не попал в группу, для которой не был предназначен."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group2.slug})
        )
        self.assertNotContains(response, self.post_with_group)

    def test_paginator_first_page(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']),
            self.COUNT_POST_IN_PAGE
        )

    def test_paginator_last_page(self):
        url_last_page = '?page=' + str(
            Post.objects.all().count() // self.COUNT_POST_IN_PAGE + 1
        )
        response = self.guest_client.get(
            reverse('posts:index') + url_last_page
        )
        self.assertEqual(
            len(response.context['page_obj']),
            Post.objects.all().count() % self.COUNT_POST_IN_PAGE
        )