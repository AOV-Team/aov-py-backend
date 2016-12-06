from apps.account.models import Gear, Profile, User
from django.test import TestCase


class TestGear(TestCase):
    """
    Test Gear model
    """
    def test_gear_all_successful(self):
        """
        Test that we can get all gear

        :return: None
        """
        user = User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = Gear(profile, [
            {
                'name': 'Canon T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'name': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            }
        ])
        gear.save()

        items = gear.all

        self.assertEquals(len(items), 2)
        self.assertEquals(items[0]['name'], 'Canon T3i')

    def test_gear_all_empty(self):
        """
        Test that empty gear list returns empty list

        :return: None
        """
        user = User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = Gear(profile)
        gear.save()

        items = gear.all

        self.assertIsInstance(items, list)
        self.assertEquals(len(items), 0)

    def test_gear_save_successful(self):
        """
        Test that we can save gear

        :return: None
        """
        user = User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = Gear(profile, [
            {
                'name': 'Canon T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'name': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            },
            {
                'name': 'Canon EF 50mm',
                'link': 'https://www.amazon.com/Canon-50mm-1-8-Camera-Lens/dp/B00007E7JU'
            }
        ])
        gear.save()

        items = gear.all

        self.assertEquals(len(items), 3)
        self.assertEquals(items[0]['name'], 'Canon T3i')

    def test_gear_save_empty(self):
        """
        Empty gear needs to save empty list

        :return: None
        """
        user = User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = Gear(profile)
        profile = gear.save()

        items = gear.all

        self.assertIsInstance(items, list)
        self.assertEquals(len(items), 0)

        # Check profile
        self.assertEquals(profile.gear, '[]')
