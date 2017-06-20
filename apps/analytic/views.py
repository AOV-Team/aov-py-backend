from apps.account import models as account_models
from apps.analytic import dates
from apps.common.views import get_default_response
from apps.photo import models as photo_models
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
import statistics


@staff_member_required
def statistics_admin(request):
    """
    Advanced user and photo stats

    :param request: Request object
    :return: render()
    """
    ages = list()
    photos = list()

    # Age
    users = account_models.User.objects.filter(is_active=True).annotate(Count('photo'))

    for u in users:
        if u.age:
            ages.append(u.age)

        # Photos per user
        photos.append(u.photo__count)

    # Feed stats
    feeds = photo_models.PhotoFeed.objects.filter(public=True)

    for feed in feeds:
        photo_counts = 0

        feed_photos = photo_models.Photo.objects.filter(photo_feed__id=feed.id)

        for photo in feed_photos:
            photo_counts += photo.user_action.filter(action='photo_click').count()

        feed.total_clicks = photo_counts

    context = {
        'age_avg': round(statistics.mean(ages), 2),
        'age_high': max(int(age) for age in ages),
        'age_low': min(int(age) for age in ages),
        'avg_photos': round(statistics.mean(photos), 2),
        'feeds': feeds
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
