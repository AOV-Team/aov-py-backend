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
        # Set up message
        message = post['message']
        recipient = post['recipient']
    else:
        pass

    context = {}

    return render(request, 'push_notification_manager.html', context)