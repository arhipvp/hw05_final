from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.test_group_data = {
            'title': 'Тестовая группа',
            'slug': 'Тестовый слаг',
            'description': 'Тестовое описание',
        }
        cls.POST_LEN_FOR_STR = 15
        cls.test_post_data = {
            'author': cls.user,
            'text': 'Тестовый постТестовый постТестовый по постТестовый пост',
        }
        cls.test_group = Group.objects.create(**cls.test_group_data)
        cls.test_post = Post.objects.create(**cls.test_post_data)

    def test_models_have_correct_object_names(self):
        """У моделей корректно работает __str__."""
        self.assertEqual(
            str(self.test_group), self.test_group_data['title']
        )
        self.assertEqual(
            str(self.test_post),
            self.test_post_data['text'][:self.POST_LEN_FOR_STR]
        )

    def test_models_have_correct_verbose_name_and_helptext(self):
        """У моделей корректно работает verbose_name и helptext"""
        self.assertEqual(
            self.test_post._meta.get_field('author').verbose_name, 'Author'
        )
        self.assertEqual(
            self.test_post._meta.get_field('author').help_text, 'Автор'
        )
