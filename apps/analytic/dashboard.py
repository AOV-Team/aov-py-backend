from apps.account import models as account_models
from apps.photo import models as photo_models
from datetime import datetime, timedelta
from jet.dashboard.modules import DashboardModule


class AppStatistics(DashboardModule):
    deletable = False
    title = 'App Statistics'
    template = 'admin/widgets/app-statistics.html'
    data = dict()

    def init_with_context(self, context):
        # Date calculations
        now = datetime.now()
        this_month = datetime(year=now.year, month=now.month, day=1)

        this_week = now - timedelta(days=now.weekday())
        this_week = datetime(year=this_week.year, month=this_week.month, day=this_week.day)

        today = datetime(year=now.year, month=now.month, day=now.day)

        # Photo data
        photos = photo_models.Photo.objects.all()
        photos_this_month = photos.filter(created_at__gte=this_month)
        photos_this_week = photos.filter(created_at__gte=this_week)
        photos_today = photos.filter(created_at__gte=today)

        # User data
        users = account_models.User.objects.all()
        users_this_month = users.filter(created_at__gte=this_month)
        users_this_week = users.filter(created_at__gte=this_week)
        users_today = users.filter(created_at__gte=today)

        self.data = {
            'photos_this_month': len(photos_this_month),
            'photos_this_week': len(photos_this_week),
            'photos_today': len(photos_today),
            'total_photos': len(photos),
            'total_users': len(users),
            'users_this_month': len(users_this_month),
            'users_this_week': len(users_this_week),
            'users_today': len(users_today),
        }
