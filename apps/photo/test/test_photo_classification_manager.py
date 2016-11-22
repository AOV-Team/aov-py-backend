from apps.photo import models as photo_models
from django.test import TestCase


class TestPhotoClassificationManager(TestCase):
    def test_create_photo_classification_successful(self):
        """
        Test that we can create a new classification

        :return: None
        """
        photo_models.PhotoClassification.objects.create_or_update(name='Landscape')

        query = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(query), 1)
        self.assertEquals(query[0].name, 'Landscape')
        self.assertEquals(query[0].classification_type, 'tag')  # default is tag

    def test_create_photo_classifications_successful(self):
        """
        Test that we can create 2 distinct classifications

        :return: None
        """
        photo_models.PhotoClassification.objects.create_or_update(name='Landscape')
        photo_models.PhotoClassification.objects.create_or_update(name='Abstract')

        query = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(query), 2)

    def test_create_photo_classifications_update_case(self):
        """
        Test that a classification created with a different case updates instead of creating a new entry

        :return: None
        """
        photo_models.PhotoClassification.objects.create_or_update(name='Landscape')

        query = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(query), 1)

        # This must update existing entry
        photo_models.PhotoClassification.objects.create_or_update(name='landscape')

        query2 = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(query2), 1)
        self.assertEquals(query2[0].name, 'landscape')

    def test_create_photo_classifications_update_case_different_classifications(self):
        """
        Test that a classification created with same name but different type creates a new entry

        :return: None
        """
        photo_models.PhotoClassification.objects.create_or_update(name='Landscape', classification_type='category')

        query = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(query), 1)

        # This must not update existing entry
        photo_models.PhotoClassification.objects.create_or_update(name='landscape')

        query2 = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(query2), 2)
