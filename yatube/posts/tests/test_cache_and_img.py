import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='Author')
        cls.user_commentator = User.objects.create_user(username='Commentator')
        cls.group_test = Group.objects.create(
            title='Тестовая группа',
            slug='Grouptest',
            description='testtesttesttesttest'
        )

        cls.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        cls.uploaded = SimpleUploadedFile(
            name='test_small.gif',
            content=cls.image,
            content_type='image/gif'
        )

        cls.post_with_img = Post.objects.create(
            text='TESTOVIEEEEEE',
            author=cls.user_author,
            image=cls.uploaded,
            group=cls.group_test,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user_author)
        self.commentator_client = Client()
        self.commentator_client.force_login(self.user_commentator)
        cache.clear()

    def test_sorl_thumbnail_index(self):
        """Пост с картинкой передаётся в словаре context (profile)"""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertIn(
            self.uploaded.name, response.context['page_obj'][0].image.name
        )

    def test_sorl_thumbnail_profile(self):
        """Пост с картинкой передаётся в словаре context (profile)"""
        response = self.guest_client.get(
            reverse(
                'posts:profile', kwargs={'username': self.user_author.username}
            )
        )
        self.assertIn(
            self.uploaded.name, response.context['page_obj'][0].image.name
        )

    def test_sorl_thumbnail_group(self):
        """Пост с картинкой передаётся в словаре context (group_list)"""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_test.slug})
        )
        self.assertIn(
            self.uploaded.name, response.context['page_obj'][0].image.name
        )

    def test_sorl_thumbnail_post_detail(self):
        """Пост с картинкой передаётся в словаре context (post_detail)"""
        response = self.guest_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post_with_img.pk}
            )
        )
        self.assertIn(
            self.uploaded.name, response.context['post'].image.name
        )

    def test_sorl_thumbnail_PostForm(self):
        """при отправке поста с картинкой через форму
        PostForm создаётся запись в базе данных"""
        form_data = {
            'text': 'Текст для проверки PostForm и картинки',
            'group': self.group_test.pk,
            'image': self.uploaded.name,
        }
        self.author_client.post(reverse('posts:post_create'), data=form_data)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
        ).exists())

    def test_cache_page(self):
        """Список постов на главной странице сайта хранится в кэше"""
        test_post_cache = Post.objects.create(
            text='Тест для проверки кэширования',
            author=self.user_author,
        )
        response = self.guest_client.get(reverse('posts:index'))
        test_post_cache.delete()
        response_cache = self.guest_client.get(reverse('posts:index'))

        self.assertEqual(response.content, response_cache.content)

        cache.clear()
        response_cache = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, response_cache.content)

    def test_404(self):
        """404 отдаёт кастомный шаблон."""
        response = self.guest_client.get('/nothingpage')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_1(self):
        """Авторизованный пользователь может
        подписываться на других пользователей и удалять их из подписок."""

        self.commentator_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_author.username}
            )
        )
        self.assertTrue(
            Follow.objects.filter(author=self.user_author).exists()
        )

        self.commentator_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_author.username}
            )
        )
        self.assertFalse(
            Follow.objects.filter(author=self.user_author).exists()
        )

    def test_2(self):
        """
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан.
        """
        test_post_follow = Post.objects.create(
            text='Тестовый пост для follow',
            author=self.user_author,
        )
        test_follow = Follow.objects.create(
            user=self.user_commentator,
            author=self.user_author
        )
        response = self.commentator_client.get(reverse('posts:follow_index'))
        self.assertContains(response, test_post_follow.text)

        test_follow.delete()
        response = self.commentator_client.get(reverse('posts:follow_index'))
        self.assertNotContains(response, test_post_follow.text)
