from apps.common.models import EditMixin
from django.db import models


class Quote(EditMixin):
    """
    Model to store a given Quote
    """
    quote = models.TextField()
    author = models.CharField(max_length=128)
    display_date = models.DateField(unique=True)

    def __str__(self):
        return "{}... - {}".format(self.quote[:20], self.author)

    class Meta:
        verbose_name_plural = "Quotes"


class QuoteSubscriber(EditMixin):
    """
    Model to track who has subscribed to receive Quotes
    """

    email = models.EmailField(unique=True)

    def __str__(self):
        return "{} - {}".format(self.pk, self.email)

    class Meta:
        verbose_name_plural = "Quote Subscribers"
