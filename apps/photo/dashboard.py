from apps.photo import models as photo_models
from django.db.models import Count
from jet.dashboard.modules import DashboardModule


class CategoriesOverview(DashboardModule):
    title = 'Most Active Categories'
    template = 'admin/widgets/categories-overview.html'
    limit = 20

    def init_with_context(self, context):
        self.children = photo_models.PhotoClassification.objects\
            .filter(classification_type='category').annotate(photos=Count('category')).order_by('-photos')[:self.limit]


class RecentPhotos(DashboardModule):
    title = 'Recent Photos'
    template = 'admin/widgets/recent-photos.html'
    limit = 8

    def init_with_context(self, context):
        self.children = photo_models.Photo.objects.order_by('-id')[:self.limit]
