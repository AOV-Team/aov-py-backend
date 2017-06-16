from apps.photo import forms as photo_forms
from apps.photo import models as photo_models
from django.forms import ValidationError
from django.test import TestCase


class TestPhotoClassificationAdminForm(TestCase):
    """
        Test class to validate correct functionality of the PhotoClassificationAdminForm
    """
    def test_photo_classification_admin_form_clean_controls_admin_order_value_uniqueness_tag(self):
        """
            Unit test to validate that clean() method of PhotoClassificationAdmin class does not allow the same order
            value for tags
        :return: No return value
        """
        form_data = {
            'classification_type': 'tag',
            'name': 'test_tag',
            'public': True,
            'admin_order_value': 1
        }
        form = photo_forms.PhotoClassificationAdminForm(form_data)
        form.is_valid()  # Necessary to generated the cleaned_data needed for the next call
        cleaned = form.clean()

        self.assertEqual(cleaned.get('admin_order_value'), form_data['admin_order_value'])

        # Save the above object to the database to simulate what would happen in the admin
        photo_models.PhotoClassification.objects.create_or_update(**form_data)

        # Attempt to add another tag with the same order_value
        form_data['name'] = 'second_tag'
        second_form =  photo_forms.PhotoClassificationAdminForm(form_data)
        second_form.is_valid()

        with self.assertRaises(ValidationError):
            second_form.clean()

    def test_photo_classification_admin_form_clean_controls_admin_order_value_uniqueness_category(self):
        """
            Unit test to validate that clean() method of PhotoClassificationAdmin class does not allow the same order
            value for categories
        :return: No return value
        """
        form_data = {
            'classification_type': 'category',
            'name': 'test_category',
            'public': True,
            'admin_order_value': 1
        }
        form = photo_forms.PhotoClassificationAdminForm(form_data)
        form.is_valid()  # Necessary to generated the cleaned_data needed for the next call
        cleaned = form.clean()

        self.assertEqual(cleaned.get('admin_order_value'), form_data['admin_order_value'])

        # Save the above object to the database to simulate what would happen in the admin
        photo_models.PhotoClassification.objects.create_or_update(**form_data)

        # Attempt to add another tag with the same order_value
        form_data['name'] = 'second_category'
        second_form = photo_forms.PhotoClassificationAdminForm(form_data)
        second_form.is_valid()

        with self.assertRaises(ValidationError):
            second_form.clean()

    def test_photo_classification_admin_form_clean_allows_same_order_value_with_different_classifications(self):
        """
            Unit test to validate that clean() method of PhotoClassificationAdmin class correctly controls unique
            values of admin_order_value field, per classification type.
        :return: No return value
        """
        form_data = {
            'classification_type': 'category',
            'name': 'test_category',
            'public': True,
            'admin_order_value': 1
        }
        form = photo_forms.PhotoClassificationAdminForm(form_data)
        form.is_valid() # Necessary to generated the cleaned_data needed for the next call
        cleaned = form.clean()

        self.assertEqual(cleaned.get('admin_order_value'), form_data['admin_order_value'])

        # Save the above object to the database to simulate what would happen in the admin
        photo_models.PhotoClassification.objects.create_or_update(**form_data)

        # Attempt to add a tag with the same order_value
        tag_form_data = {
            'classification_type': 'tag',
            'name': 'test_tag',
            'public': True,
            'admin_order_value': 1
        }
        tag_form = photo_forms.PhotoClassificationAdminForm(tag_form_data)
        tag_form.is_valid()
        tag_cleaned = tag_form.clean()

        self.assertEqual(tag_cleaned.get('admin_order_value'), tag_form_data['admin_order_value'])

    def test_photo_classification_admin_form_clean_allows_different_order_values(self):
        """
            Unit test to validate that form allows order_values to be set in any order, just not same values per
            classification_type
        :return: No return value
        """
        form_data = {
            'classification_type': 'tag',
            'name': 'test_tag',
            'public': True,
            'admin_order_value': 1
        }
        form = photo_forms.PhotoClassificationAdminForm(form_data)
        form.is_valid()  # Necessary to generated the cleaned_data needed for the next call
        cleaned = form.clean()

        self.assertEqual(cleaned.get('admin_order_value'), form_data['admin_order_value'])

        # Save the above object to the database to simulate what would happen in the admin
        photo_models.PhotoClassification.objects.create_or_update(**form_data)

        # Attempt to add another tag with the same order_value
        form_data['name'] = 'second_tag'
        form_data['admin_order_value'] = 2
        second_form = photo_forms.PhotoClassificationAdminForm(form_data)
        second_form.is_valid()
        second_cleaned = second_form.clean()

        self.assertEqual(second_cleaned.get('admin_order_value'), form_data['admin_order_value'])
