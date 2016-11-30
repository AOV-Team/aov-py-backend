from apps.photo import models as photo_models
from django.test import TestCase


class TestPhotoClassificationManager(TestCase):
    def test_create_photo_classification_successful(self):
        """
        Test that we can create a new classification

        :return: None
        """
        photo_models.PhotoClassification.objects.create_or_update(name='Rural')

        query = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(query), 12)
        self.assertEquals(query[11].name, 'Rural')
        self.assertEquals(query[11].classification_type, 'tag')  # default is tag

    def test_create_photo_classifications_successful(self):
        """
        Test that we can create 2 distinct classifications

        :return: None
        """
        photo_models.PhotoClassification.objects.create_or_update(name='Rural')
        photo_models.PhotoClassification.objects.create_or_update(name='Abstract')

        query = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(query), 13)

    def test_create_photo_classifications_update_case(self):
        """
        Test that a classification created with a different case updates instead of creating a new entry

        :return: None
        """
        photo_models.PhotoClassification.objects.create_or_update(name='Rural')

        query = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(query), 12)

        # This must update existing entry
        photo_models.PhotoClassification.objects.create_or_update(name='rural')

        query2 = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(query2), 12)
        self.assertEquals(query2[11].name, 'rural')

    def test_create_photo_classifications_update_case_different_classifications(self):
        """
        Test that a classification created with same name but different type creates a new entry

        :return: None
        """
        photo_models.PhotoClassification.objects.create_or_update(name='Rural', classification_type='category')

        query = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(query), 12)

        # This must not update existing entry
        photo_models.PhotoClassification.objects.create_or_update(name='rural')

        query2 = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(query2), 13)
