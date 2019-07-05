from apps.account import models as account_models
from apps.photo.models import Photo, PhotoComment, PhotoClassification
from apps.photo.photo import Photo as Image
from django.test import TestCase, override_settings
from rest_framework.test import APIClient


class TestAOVWebTopUserViewGET(TestCase):
    """
    Test /api/users/{}
    """
    @override_settings(REMOTE_IMAGE_STORAGE=False)
    def test_aov_web_user_view_get_successful(self):
        """
        Test that we can get user data

        :return: None
        """
        # Create test data
        # weight of 1
        user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io', first_name='Martin',
                                                       last_name='Ronquillo', location='Boise',
                                                       social_name='@ronquilloaeon', password='pass',
                                                       username='aov_hov')
        # weight of 6
        other_user = account_models.User.objects.create_user(email="test@test.com", password="test", username="testy")
        category = PhotoClassification.objects.create_or_update(name='Test', classification_type='category')


        photo1 = Photo(image=Image(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category.set([category])
        photo1.save()
        PhotoComment.objects.create_or_update(photo=photo1, comment="Nice one!", user=other_user)

        photo2 = Photo(image=Image(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=other_user)
        photo2.save()
        photo2.category.set([category])
        photo2.save()

        request = APIClient().get('/api/aov-web/users/top', format='json')
        results = request.data["results"]

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], other_user.id)
        self.assertEqual(results[1]["id"], user.id)
