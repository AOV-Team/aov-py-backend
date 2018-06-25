from django.utils import timezone
from rest_framework import serializers

def setup_eager_loading(get_queryset):
    def decorator(self):
        queryset = get_queryset(self)
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset

    return decorator


def determine_render(context):
    width = int(context["request"].query_params.get("width"))
    height = int(context["request"].query_params.get("height"))

    if 246 <= width < 272:
        render_string = "image_tiny_246"
    elif 272 <= width < 640:
        render_string = "image_tiny_272"
    elif 640 <= width < 750:
        render_string = "image_small"
    elif 750 <= width < 1242:
        render_string = "image_small_2"
    elif 1242 <= width < 2048:
        render_string = "image_medium"
    else:
        render_string = "image"

    if width > 0:
        ratio = height / width
    else:
        ratio = 1.0

    render_width, render_height = size_for(width, height, ratio)
    render_dimensions = {
        "width": render_width,
        "height": render_height
    }

    if fits(width, height, render_dimensions):
        return render_string


def size_for(width, height, ratio):
    return width, width * ratio


def fits(width, height, render_dimensions):
    return width <= render_dimensions["width"] and height <= render_dimensions["height"]


class DateTimeFieldWithTZ(serializers.DateTimeField):
    """
        Class to make output of a DateTime Field timezone aware

        Reference: https://fixes.co.za/django/make-django-rest-framework-date-time-fields-timezone-aware/
    :author: gallen
    """
    def to_representation(self, value):
        value = timezone.localtime(value)
        return super(DateTimeFieldWithTZ, self).to_representation(value)


