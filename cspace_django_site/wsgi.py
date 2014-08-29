import os
import sys
import django.core.handlers.wsgi
 
path='/usr/local/share/django/bampfa_project'
 
if path not in sys.path:
    sys.path.append(path)
 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspace_django_site.settings")

#
# By setting a WSGI_BASE value in the environment, the target application
# can detect the path for the WSGI's Apache mount point.  This value must
# correspond the the value used to set Apache's WSGIScriptAlias mount point.
#
WSGI_BASE = '/bampfa_project'
os.environ.setdefault("cspace_django_site.WSGI_BASE", WSGI_BASE)
 
application = django.core.handlers.wsgi.WSGIHandler()
