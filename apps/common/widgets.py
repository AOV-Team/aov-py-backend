from django import forms
from django.conf import settings
from django.utils import safestring


class ImagePreviewWidget(forms.Widget):
    def __init__(self, attrs={}):
        self.attrs = attrs

    def render(self, name, value, attrs=None):
        """
        Render image preview

        :param name:
        :param value:
        :param attrs:
        :return: HTML String
        """
        html = '<img style="width: 25%; max-width: 300px;" src="{}{}">'\
            .format(settings.MEDIA_URL, self.attrs.get('media_path'))

        return safestring.mark_safe(html)

