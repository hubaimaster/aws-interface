from django.test import TestCase


class AuthTestCase(TestCase):
    def setUp(self):
        self.x = 1

    def test_login(self):
        self.assertEqual(self.x, 1)