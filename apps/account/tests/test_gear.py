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
                'make': 'Canon',
                'model': 'T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'make': 'Manfrotto',
                'model': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            }
        ])
        gear.save()

        items = gear.all

        self.assertEquals(len(items), 2)
        self.assertEquals(items[0]['make'], 'Canon')
        self.assertEquals(items[0]['model'], 'T3i')

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

    def test_gear_links_valid(self):
        """
        Test that links are valid

        :return: None
        """
        user = User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = Gear(profile, [
            {
                'make': 'Canon',
                'model': 'T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'make': 'Manfrotto',
                'model': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            }
        ])
        gear.save()

        payload = [
            {
                'make': 'Canon',
                'model': 'T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'make': 'Manfrotto',
                'model': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            },
            {
                'make': 'Canon',
                'model': 'EF 50mm'
            }
        ]

        self.assertTrue(gear.links_valid(payload))

    def test_gear_links_valid_changed(self):
        """
        Test that we get False if links have changed

        :return: None
        """
        user = User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = Gear(profile, [
            {
                'make': 'Canon',
                'model': 'T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'make': 'Manfrotto',
                'model': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            }
        ])
        gear.save()

        payload = [
            {
                'make': 'Canon',
                'model': 'T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'make': 'Manfrotto',
                'model': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/?'
            }
        ]

        self.assertFalse(gear.links_valid(payload))

    def test_gear_links_valid_new(self):
        """
        Test that links don't test as valid if a new link has been added

        :return: None
        """
        user = User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = Gear(profile, [
            {
                'make': 'Canon',
                'model': 'T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'make': 'Manfrotto',
                'model': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            }
        ])
        gear.save()

        payload = [
            {
                'make': 'Canon',
                'model': 'T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'make': 'Manfrotto',
                'model': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            },
            {
                'make': 'Canon',
                'model': 'EF 50mm',
                'link': 'https://www.amazon.com/gp/product/CT453446D/'
            }
        ]

        self.assertFalse(gear.links_valid(payload))

    def test_gear_links_valid_bad_data(self):
        """
        Test that we get ValueError if data to check is not valid (e.g. missing make)

        :return: None
        """
        user = User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = Gear(profile, [
            {
                'make': 'Canon',
                'model': 'T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'make': 'Manfrotto',
                'model': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            }
        ])
        gear.save()

        payload = [
            {
                'model': 'T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'make': 'Manfrotto',
                'model': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            },
            {
                'make': 'Canon',
                'model': 'EF 50mm',
                'link': 'https://www.amazon.com/gp/product/CT453446D/'
            }
        ]

        with self.assertRaises(ValueError):
            gear.links_valid(payload)

    def test_gear_save_successful(self):
        """
        Test that we can save gear

        :return: None
        """
        user = User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = Gear(profile, [
            {
                'make': 'Canon',
                'model': 'T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'make': 'Manfrotto',
                'model': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            },
            {
                'make': 'Canon',
                'model': 'EF 50mm',
                'link': 'https://www.amazon.com/Canon-50mm-1-8-Camera-Lens/dp/B00007E7JU'
            }
        ])
        gear.save()

        items = gear.all

        self.assertEquals(len(items), 3)
        self.assertEquals(items[0]['make'], 'Canon')
        self.assertEquals(items[0]['model'], 'T3i')

    def test_gear_save_bad_key(self):
        """
        Test that we cannot save data if there's an invalid key.
        Only make/model/link allowed

        :return: None
        """
        user = User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = Gear(profile, [
            {
                'make': 'Canon',
                'model': 'T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'make': 'Manfrotto',
                'model': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            },
            {
                'name': 'Canon',
                'link': 'https://www.amazon.com/Canon-50mm-1-8-Camera-Lens/dp/B00007E7JU'
            }
        ])

        with self.assertRaises(ValueError):
            gear.save()

    def test_gear_save_no_make(self):
        """
        Test that we cannot save gear without make

        :return: None
        """
        user = User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = Profile.objects.create_or_update(user=user, bio='I am a tester.')

        with self.assertRaises(ValueError):
            gear = Gear(profile, [
                {
                    'model': 'T3i'
                },
                {
                    'make': 'Manfrotto',
                    'model': 'Tripod',
                    'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
                }
            ])
            gear.save()

    def test_gear_save_no_model(self):
        """
        Test that we cannot save gear without model

        :return: None
        """
        user = User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = Profile.objects.create_or_update(user=user, bio='I am a tester.')

        with self.assertRaises(ValueError):
            gear = Gear(profile, [
                {
                    'make': 'Canon'
                },
                {
                    'make': 'Manfrotto',
                    'model': 'Tripod',
                    'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
                }
            ])
            gear.save()

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
