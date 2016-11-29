from apps.common import widgets
from django.forms import Field


class PhotoPreviewField(Field):
    disabled = False
    help_text = None
    initial = None
    label = None
    label_suffix = None
    localize = False
    required = False
    show_hidden_initial = False
    validators = []
    widget = widgets.ImagePreviewWidget

    def __init__(self, widget=None, **kwargs):
        widget = widget or self.widget

        if isinstance(widget, type):
            widget = widget()

        extra_attrs = self.widget_attrs(widget, {'media_path': kwargs.get('media_path')})

        if extra_attrs:
            widget.attrs.update(extra_attrs)

        self.widget = widget

    def widget_attrs(self, widget, default=None):
        if default:
            return default
        else:
            return {'media_path': ''}
