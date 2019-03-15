from apps.common.views import get_default_response, DefaultResultsSetPagination
from apps.quote.models import Quote
from apps.quote.serializers import QuoteSerializer, QuoteSubscriberSerializer
from django.utils import timezone
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import AllowAny


class QuoteView(ListAPIView):
    """
    Endpoint to return current Quote for the day

    /api/aov-web/quotes
    """

    permission_classes = (AllowAny,)
    serializer_class = QuoteSerializer

    def get_queryset(self):
        today = timezone.now().date()
        return Quote.objects.filter(display_date=today)


class QuoteSubscriberView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = QuoteSubscriberSerializer
