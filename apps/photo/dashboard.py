from apps.photo import models as photo_models
from jet.dashboard.modules import DashboardModule


class RecentPhotos(DashboardModule):
    title = 'Recent Photos'
    template = 'admin/widgets/recent-photos.html'
    limit = 8

    def init_with_context(self, context):
        self.children = photo_models.Photo.objects.order_by('-id')[:self.limit]
