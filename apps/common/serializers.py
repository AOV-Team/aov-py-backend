from django.utils import timezone
from rest_framework import serializers

def setup_eager_loading(get_queryset):
    def decorator(self):
        queryset = get_queryset(self)
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset

    return decorator


def determine_render(obj, context):



def sizeFor()

def fits()


class DateTimeFieldWithTZ(serializers.DateTimeField):
    """
        Class to make output of a DateTime Field timezone aware

        Reference: https://fixes.co.za/django/make-django-rest-framework-date-time-fields-timezone-aware/
    :author: gallen
    """
    def to_representation(self, value):
        value = timezone.localtime(value)
        return super(DateTimeFieldWithTZ, self).to_representation(value)


