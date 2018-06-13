from apps.account.models import UserSession
from datetime import datetime
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin


class UserSessionMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        ignored_path_list = ["admin", "logging", "jet"]
        path = request.get_full_path()
        user = getattr(request, "user", None)

        # Type check to avoid dealing with AnonymousUser requests
        if type(user) != AnonymousUser and all([ignored not in path for ignored in ignored_path_list]):
            current_date = datetime.now().date()
            user.last_login = current_date
            user.save()
            if not request.session.session_key:
                request.session.save()
            existing_session = UserSession.objects.filter(user=user).order_by("-created_at").first()
            if existing_session:
                session_creation = existing_session.created_at

                if not all([current_date.day == session_creation.day,
                            current_date.month == session_creation.month,
                            current_date.year == session_creation.year]):
                    UserSession.objects.create_or_update(user=user, session_key=request.session.session_key)
            else:
                UserSession.objects.get_or_create(user=user, session_key=request.session.session_key)

        return response