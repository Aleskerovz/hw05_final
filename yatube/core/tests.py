from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class PostsUrlsTest(TestCase):
    def test_404_page_template(self):
        """Проверяет, что страница 404 отдаёт кастомный шаблон."""
        url = reverse('posts:index') + 'non-existent-url/'
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'core/404.html')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
