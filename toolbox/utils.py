import re
import time, datetime
import csv
import solr
import cgi
import logging
from os import path

from common import cspace # we use the config file reading function
from cspace_django_site import settings

# global variables

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)
logger.info('%s :: %s :: %s' % ('toolbox startup', '-', '-'))

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'toolbox')
apps = config.get('info','apps')


def loginfo(infotype, context, request):
    logdata = ''
    #user = getattr(request, 'user', None)
    if request.user and not request.user.is_anonymous():
        username = request.user.username
    else:
        username = '-'
    if 'count' in context:
        count = context['count']
    else:
        count = '-'
    if 'querystring' in context:
        logdata = context['querystring']
    if 'url' in context:
        logdata += ' :: %s' % context['url']
    logger.info('%s :: %s :: %s :: %s' % (infotype, count, username, logdata))


def setConstants(context):

    context['timestamp'] = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

    return context


def getfromXML(element,xpath):
    result = element.find(xpath)
    if result is None: return ''
    result = '' if result.text is None else result.text
    result = re.sub(r"^.*\)'(.*)'$", "\\1", result)
    return result

def doApp(context):

    if context['appname'] == 'packinglist':
        context['fields'] = [
            {'label': 'Start', 'name': 'start'},
            {'label': 'End', 'name': 'end' }
        ]


    return context

def getAppList():
    return apps.split(',')