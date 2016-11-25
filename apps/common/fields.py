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

    def __init__(self, **kwargs):
        print('kwargs', kwargs)
        # kwargs['media_path'] = 'images/1480095395_LcRH5o.jpg'
        widget = widgets.ImagePreviewWidget(attrs=kwargs)

        # extra_attrs = self.widget_attrs(widget)
        #
        # if extra_attrs:
        #     widget.attrs.update(extra_attrs)

        self.widget = widget

        # widget = self.widget
        #
        # media_path = 'images/1480095395_LcRH5o.jpg'
        #
        # if isinstance(widget, type):
        #     widget = widget(attrs={'media_path': media_path})
        #
        # widget.media_path = media_path
        #
        # # # widget.media_path = media_path
        # # print('mppp', media_path)
        # # # media_path = 'images/1480095395_LcRH5o.jpg'
        # # # print('m000', media_path)
        # # widget = widgets.ImagePreviewWidget(attrs={'media_path': mm})
        #
        # extra_attrs = self.widget_attrs(widget)
        #
        # if extra_attrs:
        #     widget.attrs.update(extra_attrs)
        #
        # self.widget = widget
