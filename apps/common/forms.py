from apps.common import fields
from django import forms


def get_image_preview_form(dynamic_model, image_attribute_name='image'):
    class ImagePreviewForm(forms.ModelForm):
        image_preview = fields.PhotoPreviewField()

        def __init__(self, *args, **kwargs):
            super(ImagePreviewForm, self).__init__(*args, **kwargs)
            instance = getattr(self, 'instance', None)

            # If there's an instance, get image media path
            if instance and instance.pk:
                self.image_preview = fields.PhotoPreviewField(media_path=str(getattr(instance, image_attribute_name)))

        class Meta:
            fields = '__all__'
            model = dynamic_model

    return ImagePreviewForm
