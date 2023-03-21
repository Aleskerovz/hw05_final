from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_author_page_accessible_by_name(self):
        """Страница 'about:author' доступна по имени."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech_page_accessible_by_name(self):
        """Страница 'about:tech' доступна по имени."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_uses_correct_template(self):
        """Шаблон 'about/author.html' используется
        для страницы 'about:author'."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertTemplateUsed(response, 'about/author.html')

    def test_tech_uses_correct_template(self):
        """Шаблон 'about/tech.html' используется для страницы 'about:tech'."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertTemplateUsed(response, 'about/tech.html')
