from apps.photo.dashboard import RecentPhotos
from jet.dashboard.dashboard import Dashboard


class AOVDashboard(Dashboard):
    columns = 2

    def init_with_context(self, context):
        self.children.append(RecentPhotos)
