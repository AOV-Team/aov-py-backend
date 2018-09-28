from apps.account.models import UserSession
from datetime import datetime
from django.contrib.auth import user_logged_in
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin


class UserSessionMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        ignored_path_list = ["admin", "logging", "jet", "api/me", "feedback"]
        path = request.get_full_path()
        user = getattr(request, "user", None)

        # Type check via toString representation to avoid dealing with AnonymousUser requests
        if user.__str__() != "AnonymousUser" and all([ignored not in path for ignored in ignored_path_list]):
            # Send the user_logged_in signal ONLY if the path is the authenticate view
            if "auth" in path:
                try:
                    # Send the user_logged_in signal
                    user_logged_in.send(sender=user.__class__, request=request, user=user)

                # NotImplementedError raised when .save() called on AnonymousUser. Somehow makes it past if, this catches it
                except NotImplementedError:
                    return response

            if not request.session.session_key:
                request.session.save()
            existing_session = UserSession.objects.filter(user=user).order_by("-created_at").first()
            if existing_session:
                current_date = datetime.now().date()
                session_creation = existing_session.created_at

                if not all([current_date.day == session_creation.day,
                            current_date.month == session_creation.month,
                            current_date.year == session_creation.year]):
                    UserSession.objects.create_or_update(user=user, session_key=request.session.session_key)
            else:
                UserSession.objects.get_or_create(user=user, session_key=request.session.session_key)

        return response