from apps.common import forms as common_forms
from apps.photo import models as photo_models
from django import forms


class PhotoClassificationAdminForm(forms.ModelForm):
    """
        Form class to allow image and icon uploads for categories, but not tags. Also controls incrementing and
        uniqueness of admin_order_value integer values.

    :return: cleaned data to be saved
    """

    def clean(self):
        cleaned_data = super(PhotoClassificationAdminForm, self).clean()

        admin_order_value = cleaned_data.get('admin_order_value', None)
        category_image = cleaned_data.get('category_image', None)
        classification_type = cleaned_data.get('classification_type', None)
        icon = cleaned_data.get('icon', None)
        name = cleaned_data.get('name', None)

        if classification_type == 'tag' and (category_image or icon):
            if self.is_valid():
                raise forms.ValidationError("PhotoClassification entries of type 'tag' "
                                            "may not have an icon or background image")

        # Check the admin_order_value and verify that one of that value doesn't currently exist. Raises ValidationError
        if admin_order_value:
            existing = photo_models.PhotoClassification.objects.filter(admin_order_value=admin_order_value,
                                                                       classification_type=classification_type)
            if existing.exists():
                existing = existing.first()

                # Check that the item being submitted is not the same as the existing one
                if existing.name != name:
                    raise forms.ValidationError('A {} already exists with an order value of {}. '
                                                'Please choose a different value.'.format(
                        classification_type, admin_order_value))

        return cleaned_data


    class Meta:
        model = photo_models.PhotoClassification
        exclude =[]