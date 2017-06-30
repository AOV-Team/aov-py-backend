"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from apps.account import views as account_views
from apps.analytic import views as analytic_views
from apps.communication import views as communication_views
from apps.photo import views as photo_views
from apps.utils import views as utils_views
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)

urlpatterns = [
    # account
    url(r'api/auth$', account_views.AuthenticateViewSet.as_view()),
    url(r'api/auth/reset$', account_views.AuthenticateResetViewSet.as_view()),
    url(r'api/auth/social$', account_views.SocialSignUpViewSet.as_view()),
    url(r'api/gear$', account_views.GearViewSet.as_view()),
    url(r'api/gear/(?P<pk>[0-9^/]+)$', account_views.GearSingleViewSet.as_view()),
    url(r'api/me$', account_views.MeViewSet.as_view()),
    url(r'api/me/profile$', account_views.MeProfileViewSet.as_view()),
    url(r'api/users$', account_views.UserViewSet.as_view()),
    url(r'api/users/(?P<pk>[0-9^/]+)$', account_views.UserSingleViewSet.as_view()),
    url(r'api/users/(?P<user_id>[0-9^/]+)/following$', account_views.UserFollowingViewSet.as_view()),
    url(r'api/users/(?P<user_id>[0-9^/]+)/followers$', account_views.UserFollowersViewSet.as_view()),
    url(r'api/users/(?P<user_id>[0-9^/]+)/followers/(?P<follower_id>[0-9^/]+)$',
        account_views.UserFollowerSingleViewSet.as_view()),
    url(r'api/users/(?P<user_id>[0-9^/]+)/location$', account_views.UserLocationViewSet.as_view()),
    url(r'api/users/(?P<user_id>[0-9^/]+)/photos$', account_views.UserPhotosViewSet.as_view()),
    url(r'api/users/(?P<pk>[0-9^/]+)/profile$', account_views.UserProfileViewSet.as_view()),
    url(r'api/users/(?P<pk>[0-9^/]+)/stars$', account_views.UserSingleStarsViewSet.as_view()),

    # Analytic
    url(r'api/statistics/(?P<resource>[a-z^/]+)$', analytic_views.StatisticsViewSet.as_view()),

    # communication
    url(r'api/devices$', communication_views.DevicesViewSet.as_view()),

    # photo
    url(r'api/photo_classifications$', photo_views.PhotoClassificationViewSet.as_view()),
    url(r'api/photo_classifications/(?P<photo_classification_id>[0-9^/]+)/photos$',
        photo_views.PhotoClassificationPhotosViewSet.as_view()),
    url(r'api/photo_feeds$', photo_views.PhotoFeedViewSet.as_view()),
    url(r'api/photo_feeds/(?P<photo_feed_id>[0-9^/]+)/photos$', photo_views.PhotoFeedPhotosViewSet.as_view()),
    url(r'api/photos$', photo_views.PhotoViewSet.as_view()),
    url(r'api/photos/(?P<pk>[0-9^/]+)$', photo_views.PhotoSingleViewSet.as_view()),
    url(r'api/photos/(?P<pk>[0-9^/]+)/caption$', photo_views.PhotoSingleCaptionViewSet.as_view()),
    url(r'api/photos/(?P<pk>[0-9^/]+)/flags', photo_views.PhotoSingleFlagsViewSet.as_view()),
    url(r'api/photos/(?P<pk>[0-9^/]+)/(?P<user_interest>stars|likes)$',
        photo_views.PhotoSingleInterestsViewSet.as_view()),

    # sample
    # url(r'api/sample_tasks', account_views.SampleTasksViewSet.as_view()),

    # utils
    url(r'api/me/actions$', utils_views.MeActionsViewSet.as_view()),

    # admin
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^admin/', admin.site.urls),
    url(r'^admin/photos/$', photo_views.photo_admin),
    url(r'^admin/photos/map/$', photo_views.photo_map_admin),
    url(r'^admin/push/$', communication_views.push_notification_manager),
    url(r'^admin/statistics/$', analytic_views.statistics_admin),
]

# DEBUG URLs
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
