from django.test import TestCase


class TestCastomPage(TestCase):
    """тестирование кастомных страниц"""

    def test_404_custom(self):
        response = self.client.get('/random/')
        self.assertTemplateUsed(response, 'core/404.html')
