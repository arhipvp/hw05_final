from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post

User = get_user_model()


class FormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.testuser = User.objects.create_user(username="TestUser")

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(
            self.testuser
        )
        self.test_data = {
            'text': 'Тестовый тектс',
        }
        cache.clear()

    def test_form_addnew(self):
        """
        При отправке валидной формы со страницы создания поста
        reverse('posts:create_post') создаётся новая запись в базе данных;
        """
        self.authorized_client.post(
            reverse('posts:post_create'), data=self.test_data
        )
        self.assertTrue(Post.objects.filter(**self.test_data).exists())

    def test_form_edit(self):
        """
        при отправке валидной формы со страницы редактирования
        поста reverse('posts:post_edit', args=('post_id',))
        происходит изменение поста с post_id в базе данных.
        """
        test_data = {
            'text': 'Тестовый текст',
            'edit_text': 'Текст измененный',
        }
        newpost = Post.objects.create(
            text=test_data['text'],
            author=self.testuser
        )
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': newpost.id}),
            data={
                'text': test_data['edit_text']
            }
        )
        edit_post = Post.objects.get(pk=newpost.id)
        self.assertEqual(newpost.id, edit_post.id)
        self.assertNotEqual(newpost.text, edit_post.text)
