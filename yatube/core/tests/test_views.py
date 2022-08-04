from django.test import TestCase, Client


class TestCastomPage(TestCase):
    """тестирование кастомных страниц"""

    def test_404_custom(self):
        response = self.client.get('/random/')
        self.assertTemplateUsed(response, 'core/404.html')

