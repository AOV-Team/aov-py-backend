from apps.account.models import Gear, Profile, User
from django.test import TestCase
from json.decoder import JSONDecodeError


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

    def test_gear_all_invalid_json(self):
        """
        Test that if json cannot be parsed, we get an error

        :return: None
        """
        user = User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = Profile.objects.create_or_update(user=user, bio='I am a tester.',
                                                   gear='[{"make": "Canon", "model": "EF 50mm"},{]')

        gear = Gear(profile)

        with self.assertRaises(JSONDecodeError):
            gear.all

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

        with self.assertRaises(KeyError):
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
                'make': 'Canon',
                'model': 'EF 50mm',
                'name': 'Nifty Fifty',
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

        with self.assertRaises(KeyError):
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

        with self.assertRaises(KeyError):
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

    def test_gear_search_successful(self):
        """
        Test that we can search gear

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

        user_2 = User.objects.create_user(email='mr@mypapaya.io', password='pass', username='aov_hovy')
        profile_2 = Profile.objects.create_or_update(user=user_2, bio='I am a tester.')

        gear = Gear(profile_2, [
            {
                'make': 'Canon',
                'model': 'EOS 7D',
                'link': 'https://shop.usa.canon.com/shop/en/catalog/eos-7d-mark-ii-body'
            },
            {
                'make': 'Canon',
                'model': 'EF-S 60mm',
                'link': 'https://shop.usa.canon.com/shop/en/catalog/ef-s-60mm-f-28-macro-usm'
            },
            {
                'make': 'Tamron',
                'model': 'SP 85mm',
                'link': 'http://www.tamron-usa.com/F016special/index.html'
            },
        ])
        gear.save()

        results = Gear.objects.search('canon')

        # print(results)
        self.assertEquals(len(results), 4)

        results = Gear.objects.search('tamron')

        self.assertEquals(len(results), 1)

    def test_gear_search_two_words(self):
        """
        Test that we can search gear if query is 2 words

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

        user_2 = User.objects.create_user(email='mr@mypapaya.io', password='pass', username='aov_hovy')
        profile_2 = Profile.objects.create_or_update(user=user_2, bio='I am a tester.')

        gear = Gear(profile_2, [
            {
                'make': 'Canon',
                'model': 'EOS 7D',
                'link': 'https://shop.usa.canon.com/shop/en/catalog/eos-7d-mark-ii-body'
            },
            {
                'make': 'Canon',
                'model': 'EF-S 60mm',
                'link': 'https://shop.usa.canon.com/shop/en/catalog/ef-s-60mm-f-28-macro-usm'
            },
            {
                'make': 'Tamron',
                'model': 'SP 85mm',
                'link': 'http://www.tamron-usa.com/F016special/index.html'
            },
        ])
        gear.save()

        results = Gear.objects.search('canon t3i')

        self.assertEquals(len(results), 1)
        self.assertEquals(results[0]['model'], 'T3i')
