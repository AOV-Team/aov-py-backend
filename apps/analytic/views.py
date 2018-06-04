from apps.account import models as account_models
from apps.analytic import dates
from apps.common.views import get_default_response
from apps.photo import models as photo_models
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg, Min, Max
from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from datetime import timedelta


@staff_member_required
def statistics_admin(request):
    """
    Advanced user and photo stats

    :param request: Request object
    :return: render()
    """

    # Age
    users = account_models.User.objects.filter(is_active=True, age__isnull=False, age__gte=1).annotate(Count('photo'))
    age_stats = users.aggregate(Avg('age'), Max('age'), Min('age'))
    photos = users.aggregate(Avg('photo__count'))

    # Feed stats
    feeds = photo_models.PhotoFeed.objects.filter(public=True)
    for feed in feeds:
        feed_photos = photo_models.Photo.objects.filter(photo_feed__id=feed.id)
        feed.votes = sum(feed_photos.values_list("votes", flat=True))

    # Power Users
    cutoff = datetime.now() - timedelta(days=7)
    sessions = account_models.UserSession.objects.filter(user__in=users, modified_at__gte=cutoff)
    power_users = account_models.User.objects.filter(id__in=sessions.values_list("user", flat=True))
    power_users_display = power_users.annotate(Count("usersession")).filter(usersession__count__gte=3)
    power_users_display = power_users_display.order_by("-usersession__count")[:25]

    context = {
        'age_avg': round(age_stats["age__avg"], 2),
        'age_high': age_stats["age__max"],
        'age_low': age_stats["age__min"],
        'avg_photos': round(photos["photo__count__avg"], 2),
        'feeds': feeds,
        'power_users': power_users_display,
        'power_users_count': power_users_display.count()
    }

    return render(request, 'statistics.html', context)


class StatisticsViewSet(APIView):
    """
    /api/statistics/{photos/users}
    This endpoint retrieves stats

    For photos:
    {
        results: [
            {
                date: '2017-01-01',
                average_photos_per_user: ##
            }
        ]
    }

    """
    authentication_classes = (SessionAuthentication,)
    queryset = photo_models.Photo.objects.all()

    def get(self, request, **kwargs):
        """
        Return stats for requested resource

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        resource = kwargs.get('resource')
        response = get_default_response('400')

        if resource == 'photos' or resource == 'users':
            if resource == 'photos':
                data_points = list()
                date_ranges = dates.get_month_date_ranges(datetime(2016, 12, 1), datetime.now())

                for d in date_ranges:
                    photos = photo_models.Photo.objects.filter(created_at__lte=d[1], public=True)
                    users = account_models.User.objects.filter(created_at__lte=d[1], is_active=True)\
                        .exclude(email='AnonymousUser')

                    data_points.append({
                        'date': '{}-{}-{}'.format(d[0].year, d[0].month, d[0].day),
                        'average_photos_per_user': round(photos.count() / users.count(), 2)
                    })

                response = get_default_response('200')
                response.data['results'] = data_points

        return response
