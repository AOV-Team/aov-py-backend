from apps.communication.tasks import send_push_notification
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render


@staff_member_required
def push_notification_manager(request):
    """
    View for /admin/push/

    :param request: Request object
    :return: render()
    """
    post = request.POST

    if len(post) > 0:
        print(post)
        # Set up message
        message = post['message']
        recipients = post['recipients']

        if recipients == 'all':
            send_push_notification.delay(message, 'all')
    else:
        pass

    context = {}

    return render(request, 'push_notification_manager.html', context)