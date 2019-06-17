from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings


DOCUMENTATION_ROOT = '/index.html'


@login_required
def documentation(request, path=''):
    if path == '':
        path = DOCUMENTATION_ROOT
    if not settings.DOCUMENTATION_ACCESS_FUNCTION(request.user):
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    with open("".join([settings.DOCUMENTATION_HTML_ROOT, path])) as file:
        return HttpResponse(file.read())
