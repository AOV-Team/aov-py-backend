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
from apps.discover import views as discover_views
from apps.photo import views as photo_views
from apps.podcast import views as podcast_views
from apps.quote import views as quote_views
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
    # url(r'api/auth/social$', account_views.SocialSignUpViewSet.as_view()),
    url(r'api/gear$', account_views.GearViewSet.as_view()),
    url(r'api/gear/(?P<pk>[0-9^/]+)$', account_views.GearSingleViewSet.as_view()),
    url(r'api/me$', account_views.MeViewSet.as_view()),
    url(r'api/me/following/photos$', photo_views.UserFollowingPhotoViewSet.as_view()),
    url(r'api/me/galleries$', photo_views.GalleryRetrieveViewSet.as_view()),
    url(r'api/me/notifications$', communication_views.UserNotificationRecordViewSet.as_view()),
    url(r'api/me/notifications/(?P<record_id>[0-9^/]+)/view$', communication_views.UserNotificationRecordViewSet.as_view()),
    url(r'api/me/profile$', account_views.MeProfileViewSet.as_view()),
    url(r'api/search/users$', account_views.UserSearchViewSet.as_view()),
    url(r'api/me/starred/photos$', account_views.UserStarredPhotosViewSet.as_view()),
    url(r'api/users$', account_views.UserViewSet.as_view()),
    url(r'api/users/(?P<pk>[0-9^/]+)$', account_views.UserSingleViewSet.as_view()),
    url(r'api/users/(?P<pk>[0-9^/]+)/blocked$', account_views.BlockUserViewSet.as_view()),
    url(r'api/users/(?P<user_id>[0-9^/]+)/following$', account_views.UserFollowingViewSet.as_view()),
    url(r'api/users/(?P<user_id>[0-9^/]+)/followers$', account_views.UserFollowersViewSet.as_view()),
    url(r'api/users/(?P<user_id>[0-9^/]+)/followers/(?P<follower_id>[0-9^/]+)$',
        account_views.UserFollowerSingleViewSet.as_view()),
    url(r'api/users/(?P<user_id>[0-9^/]+)/galleries$', photo_views.GalleryRetrieveViewSet.as_view()),
    url(r'api/users/(?P<user_id>[0-9^/]+)/galleries/(?P<gallery_id>[0-9^/]+)$', photo_views.GalleryRetrieveViewSet.as_view()),
    url(r'api/users/(?P<user_id>[0-9^/]+)/galleries/(?P<gallery_id>[0-9^/]+)/photos$', photo_views.GalleryPhotoViewSet.as_view()),
    url(r'api/users/(?P<user_id>[0-9^/]+)/location$', account_views.UserLocationViewSet.as_view()),
    url(r'api/users/(?P<user_id>[0-9^/]+)/photos$', account_views.UserPhotosViewSet.as_view()),
    url(r'api/users/(?P<pk>[0-9^/]+)/profile$', account_views.UserProfileViewSet.as_view()),
    url(r'api/users/(?P<pk>[0-9^/]+)/stars$', account_views.UserSingleStarsViewSet.as_view()),

    # Analytic
    url(r'api/statistics/(?P<resource>[a-z^/]+)$', analytic_views.StatisticsViewSet.as_view()),

    # communication
    url(r'api/conversations$', communication_views.ConversationViewSet.as_view()),
    url(r'api/devices$', communication_views.DevicesViewSet.as_view({"get": "list", "post": "post"})),
    url(r'api/users/(?P<pk>[0-9^/]+)/conversations$', communication_views.ConversationViewSet.as_view()),
    url(r'api/users/(?P<pk>[0-9^/]+)/conversations/(?P<conversation_id>[0-9^/]+)$',
        communication_views.ConversationViewSet.as_view()),
    url(r'api/users/(?P<pk>[0-9^/]+)/messages$', communication_views.DirectMessageViewSet.as_view()),
    url(r'api/users/(?P<pk>[0-9^/]+)/messages/(?P<message_pk>[0-9^/]+)/read$', communication_views.DirectMessageMarkReadViewSet.as_view()),

    # photo
    url(r'api/aov-web/photos/top$', photo_views.PhotoAppTopPhotosViewSet.as_view()),
    url(r'api/photo_classifications$', photo_views.PhotoClassificationViewSet.as_view()),
    url(r'api/photo_classifications/search$', photo_views.TagSearchViewSet.as_view()),
    url(r'api/photo_classifications/(?P<photo_classification_id>[0-9^/]+)/photos$',
        photo_views.PhotoClassificationPhotosViewSet.as_view()),
    url(r'api/photo_feeds$', photo_views.PhotoFeedViewSet.as_view()),
    url(r'api/photo_feeds/(?P<photo_feed_id>[0-9^/]+)/photos$', photo_views.PhotoFeedPhotosViewSet.as_view()),
    url(r'api/photos$', photo_views.PhotoViewSet.as_view()),
    url(r'api/photos/(?P<pk>[0-9^/]+)$', photo_views.PhotoSingleViewSet.as_view()),
    url(r'api/photos/(?P<pk>[0-9^/]+)/caption$', photo_views.PhotoSingleCaptionViewSet.as_view()),
    url(r'api/photos/(?P<pk>[0-9^/]+)/comments$', photo_views.PhotoSingleCommentViewSet.as_view()),
    url(r'api/photos/(?P<pk>[0-9^/]+)/comments/(?P<comment_id>[0-9^/]+)/replies$',
        photo_views.PhotoSingleCommentReplyViewSet.as_view()),
    url(r'api/photos/(?P<pk>[0-9^/]+)/details$', photo_views.PhotoSingleDetailsView.as_view()),
    url(r'api/photos/(?P<pk>[0-9^/]+)/flags$', photo_views.PhotoSingleFlagsViewSet.as_view()),
    url(r'api/photos/(?P<pk>[0-9^/]+)/media$', photo_views.PhotoSingleMediaView.as_view()),
    url(r'api/photos/(?P<pk>[0-9^/]+)/(?P<user_interest>stars|likes)$',
        photo_views.PhotoSingleInterestsViewSet.as_view()),
    url(r'api/photos/top$', photo_views.PhotoAppTopPhotosViewSet.as_view()),
    url(r'api/photos/(?P<pk>[0-9^/]+)/votes', photo_views.PhotoSingleVotesViewSet.as_view()),

    # sample
    # url(r'api/sample_tasks', account_views.SampleTasksViewSet.as_view()),

    # marketplace
    # url(r'api/marketplace/listings/(?P<pk>[0-9^/]+)$', marketplace_views.MarketplaceListingViewSet.as_view()),
    # url(r'api/marketplace/offers$', marketplace_views.MarketplaceOfferViewSet.as_view()),
    # url(r'api/marketplace/users$', marketplace_views.MarketplaceUserViewSet.as_view()),
    # url(r'api/marketplace/users/activate$', marketplace_views.MarketplaceActivationViewSet.as_view()),
    # url(r'api/marketplace/users/(?P<pk>[0-9^/]+)/offers$', marketplace_views.MarketplaceOfferViewSet.as_view()),

    # utils
    url(r'api/me/actions$', utils_views.MeActionsViewSet.as_view()),
    url(r'api/utils/feedback$', utils_views.FeedbackViewSet.as_view()),
    url(r'api/utils/feedback/(?P<pk>[0-9^/]+)/reply$', utils_views.FeedbackViewSet.as_view()),
    url(r'api/utils/profiles$', utils_views.APIRequestLogViewSet.as_view()),

    # logging
    url(r'api/logging/classification/(?P<photo_classification_id>[0-9^/]+)$',
        photo_views.LoggedPhotoClassificationPhotosViewSet.as_view()),
    url(r'api/logging/all_photos$', photo_views.LoggedPhotoViewSet.as_view()),
    url(r'api/logging/single_photo/(?P<pk>[0-9^/]+)$', photo_views.LoggedPhotoSingleViewSet.as_view()),
    url(r'api/logging/top_photos$', photo_views.LoggedPhotoAppTopPhotosViewSet.as_view()),
    url(r'api/logging/user_photos/(?P<user_id>[0-9^/]+)$', account_views.LoggedUserPhotosViewSet.as_view()),

    # admin

    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^admin/', admin.site.urls),
    url(r'^admin/photos/$', photo_views.photo_admin),
    url(r'^admin/photos/map/$', photo_views.photo_map_admin),
    url(r'^admin/power_users/$', account_views.power_users_admin),
    url(r'^admin/push/$', communication_views.push_notification_manager),
    url(r'^admin/statistics/$', analytic_views.statistics_admin),

    ## AOV-WEB

    # auth
    url(r'api/aov-web/auth/social$', account_views.SocialSignUpViewSet.as_view()),

    # podcast
    url(r'api/aov-web/podcast/get_featured$', podcast_views.GetFeaturedRequestView.as_view()),
    url(r'api/aov-web/podcast/episodes$', podcast_views.EpisodeViewSet.as_view()),

    # discover
    url(r'api/aov-web/discover/downloaders$', discover_views.DownloaderView.as_view()),
    url(r'api/aov-web/discover/states$', discover_views.StateView.as_view()),
    url(r'api/aov-web/discover/states/(?P<pk>[0-9^/]+)/photographers$', discover_views.StatePhotographerView.as_view()),
    url(r'api/aov-web/discover/states/(?P<pk>[0-9^/]+)/photos$', discover_views.StatePhotoView.as_view()),
    url(r'api/aov-web/discover/states/(?P<pk>[0-9^/]+)/sponsors$', discover_views.StateSponsorView.as_view()),

    # quote
    url(r'api/aov-web/quotes$', quote_views.QuoteView.as_view()),
    url(r'api/aov-web/quote-subscribers$', quote_views.QuoteSubscriberView.as_view()),

    # users
    url(r'api/aov-web/users/top$', account_views.AOVWebTopUsersView.as_view()),
    url(r'api/aov-web/users/(?P<pk>[0-9^/]+)$', account_views.AOVWebUsersView.as_view()),
    url(r'api/aov-web/users/(?P<pk>[0-9^/]+)/profile$', account_views.AOVWebUserProfileView.as_view()),
]

# DEBUG URLs
if settings.DEBUG:
    # import debug_toolbar

    # urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += [url(r'api/(?P<user_id>[0-9^/]+)/sample_login$', account_views.SampleLoginViewSet.as_view())]
