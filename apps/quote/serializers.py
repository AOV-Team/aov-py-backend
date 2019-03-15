from apps.common.serializers import DateTimeFieldWithTZ
from apps.quote import models
from rest_framework.serializers import ModelSerializer


class QuoteSerializer(ModelSerializer):
    class Meta:
        model = models.Quote
        fields = ("quote", "author", "display_date")


class QuoteSubscriberSerializer(ModelSerializer):
    created_at = DateTimeFieldWithTZ(required=False)
    modified_at = DateTimeFieldWithTZ(required=False)

    class Meta:
        model = models.QuoteSubscriber
        fields = "__all__"