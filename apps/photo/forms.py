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

        category_image = cleaned_data.get('category_image', None)
        classification_type = cleaned_data.get('classification_type', None)
        icon = cleaned_data.get('icon', None)

        if classification_type == 'tag' and (category_image or icon):
            if self.is_valid():
                raise forms.ValidationError("PhotoClassification entries of type 'tag' "
                                            "may not have an icon or background image")

        return cleaned_data


    class Meta:
        model = photo_models.PhotoClassification
        exclude =[]