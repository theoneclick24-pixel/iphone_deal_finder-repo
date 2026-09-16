from django.test import TestCase
from django.contrib.auth.models import User

class UserProfileTestCase(TestCase):
    def test_user_profile_creation_and_defaults(self):
        user = User.objects.create_user(username='testuser', password='password123')
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.operational_city, 'Maturín')
        self.assertEqual(user.profile.min_budget, 100.00)
        self.assertEqual(user.profile.max_budget, 250.00)
        self.assertEqual(user.profile.min_profit, 30.00)

    def test_user_profile_configurable_values(self):
        user = User.objects.create_user(username='trader', password='password123')
        profile = user.profile
        profile.min_profit = 50.00
        profile.max_budget = 400.00
        profile.save()

        user.refresh_from_db()
        self.assertEqual(user.profile.min_profit, 50.00)
        self.assertEqual(user.profile.max_budget, 400.00)
