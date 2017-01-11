from apps.analytic.dashboard import AppStatistics
from apps.photo.dashboard import CategoriesOverview, RecentPhotos
from jet.dashboard.dashboard import Dashboard


class AOVDashboard(Dashboard):
    columns = 2

    def init_with_context(self, context):
        self.children.append(RecentPhotos())
        self.children.append(CategoriesOverview())
        self.children.append(AppStatistics())
