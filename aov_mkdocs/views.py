from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from mimetypes import guess_type


DOCUMENTATION_ROOT = '/index.html'


@login_required
def documentation(request, path):
    if path == '':
        path = DOCUMENTATION_ROOT
    if not settings.DOCUMENTATION_ACCESS_FUNCTION(request.user):
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    # This is how the documentation files are served locally, when runserver is executed
    if not settings.DOCUMENTATION_XSENDFILE:
        with open("".join([settings.DOCUMENTATION_HTML_ROOT, path])) as file:
            return HttpResponse(file.read())

    # This is how it is served via Nginx - This will show a blank page via runserver
    mimetype, encoding = guess_type(path)
    response = HttpResponse(content_type=mimetype)

    response['Content-Encoding'] = encoding
    response['Content-Disposition'] = ''
    response['X-Sendfile'] = "".join([settings.DOCUMENTATION_HTML_ROOT,
                                      path])
    return response