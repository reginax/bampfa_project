__author__ = 'jblowe'

import os
import re
import sys
import time
import pgdb

reload(sys)
sys.setdefaultencoding('utf-8')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response

from common import cspace # we use the config file reading function
from cspace_django_site import settings
from os import path

from operator import itemgetter

from search.utils import loginfo
from common import cspace # we use the config file reading function
from cspace_django_site import settings
from cspace_django_site.main import cspace_django_site

mainConfig = cspace_django_site.getConfig()

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'authorityeditor')
TITLE = config.get('info', 'TITLE')

# alas, there are many ways the XML parsing functionality might be installed.
# the following code attempts to find and import the best...
try:
    from xml.etree.ElementTree import tostring, parse, Element, fromstring
    print("running with xml.etree.ElementTree")
except ImportError:
    try:
        from lxml import etree
        print("running with lxml.etree")
    except ImportError:
        try:
            # normal cElementTree install
            import cElementTree as etree
            print("running with cElementTree")
        except ImportError:
            try:
                # normal ElementTree install
                import elementtree.ElementTree as etree
                print("running with ElementTree")
            except ImportError:
                print("Failed to import ElementTree from any known place")


def check(request):
    parms = {}
    csidParms = True
    try:
        reportXML = parse(request)
        parameters = reportXML.findall('{http://jasperreports.sourceforge.net/jasperreports}parameter')
        #print 'parameters',parameters
        for p in parameters:
            name = p.attrib['name']
            isForPrompting = p.get('isForPrompting')
            if name == 'csid':
                csidParms = False
            try:
                default = p.find('{http://jasperreports.sourceforge.net/jasperreports}defaultValueExpression').text
            except:
                default = ''
            try:
                description = p.find('{http://jasperreports.sourceforge.net/jasperreports}parameterDescription').text
            except:
                description = ''
            parms[name] = [default.strip('"'), isForPrompting, description.strip('"')]
    except:
        #raise
        # indicate that .jrxml file was not found...
        print 'jrxml file not found, no parms extracted.'
    return parms,csidParms


def makePayload(parms):
    """
    this method takes a dictionary of parameters and inserts them into the XML payload
    which is POSTed to the report service.
    :param parms: a dict of parameters and values for the iReport
    :return: string, XML doc really, containing payload with parameters
    """
    result = fromstring('''<?xml version="1.0"?>
<ns2:invocationContext xmlns:ns2="http://collectionspace.org/services/common/invocable"
     xmlns:ns3="http://collectionspace.org/services/jaxb">
    <mode>nocontext</mode>
    <docType>CollectionObjectTenant15</docType>
    <params/>
</ns2:invocationContext>''')
    p = result.find('params')
    for k, v in parms:
        e   = Element('param')
        key = Element('key')
        val = Element('value')
        key.text = k
        val.text = v
        e.append(key)
        e.append(val)
        p.append(e)
    return tostring(result)


def findrefname(table, term, config):
    dbconn = pgdb.connect(database=config.get('connect', 'connect_string'))
    objects = dbconn.cursor()

    query = "select refname from %s where refname ILIKE '%%''%s''%%'" % (table, term.replace("'", "''"))

    try:
        objects.execute(query)
        refname = objects.fetchone()
        return [term, refname]
    except:
        raise
        return "findrefnames error"


#@login_required()
def change(request):
    connection = cspace.connection.create_connection(mainConfig, request.user)
    (url, data, statusCode) = connection.make_get_request('cspace-services/reports')
    reportXML = fromstring(data)
    reportCsids = [csidElement.text for csidElement in reportXML.findall('.//csid')]
    reportNames = [csidElement.text for csidElement in reportXML.findall('.//name')]
    fileNames = []
    #print reportCsids
    for csid in reportCsids:
        (url, data, statusCode) = connection.make_get_request('cspace-services/reports/%s' % csid)
        reportXML = fromstring(data)
        fileName = reportXML.find('.//filename')
    reportData = zip(reportCsids, reportNames, fileNames)
    reportData = sorted(reportData, key=itemgetter(1))
    return render(request, 'listReports.html', {'reportData': reportData, 'labels': 'name file'.split(' '), 'title': TITLE})


#@login_required()
def index(request):

    if request.method == 'GET' and request.GET != {}:
        context = {}

        context['title'] = TITLE

        # do search
        loginfo('start search', context, request)

        return render(request, 'index.html', context)

    else:
        return render(request, 'index.html', {'title': TITLE})
