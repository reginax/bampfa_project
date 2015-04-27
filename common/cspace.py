__author__ = 'remillet,jblowe'

from os import path
from ConfigParser import NoOptionError
import urllib2
import ConfigParser
import time
import re


CONFIG_SUFFIX = ".cfg"
CONFIGSECTION_SERVICES_CONNECT = 'cspace_services_connect'
CONFIGSECTION_AUTHN_CONNECT = 'cspace_authn_connect'
LOGIN_URL = '/accounts/login/'
LOGIN_URL_REDIRECT = LOGIN_URL + '?next=%s'
CONFIGSECTION_INFO = 'info'

CSPACE_SHOULD_RELOAD_CONFIG = 'shouldReloadConfig'
CSPACE_REALM_PROPERTY = 'realm'
CSPACE_URI_PROPERTY = 'uri'
CSPACE_HOSTNAME_PROPERTY = 'hostname'
CSPACE_PROTOCOL_PROPERTY = 'protocol'
CSPACE_PORT_PROPERTY = 'port'


def getConfig(base_path, filename_nosuffix):
    """
        Read in our config file.  Look for it to be a sibling of the current .py file (this authn.py file).
    :param filename_nosuffix:
    """
    fileName = filename_nosuffix + CONFIG_SUFFIX
    relative_path = path.join(base_path, fileName)  # config file should be one of our siblings
    config = ConfigParser.RawConfigParser()
    config.read(relative_path)
    theSections = config.sections()
    if len(theSections) is 0:
        errMsg = "Could not find the required config file %s" % relative_path
        print(errMsg)
        raise Exception(errMsg)

    return config


def getConfigOptionWithSection(config, section, property_name):
    result = None
    try:
        result = config.get(section, property_name)
    except NoOptionError:
        print "Found no option %s" % property_name

    return result


def make_get_request(realm, uri, hostname, protocol, port, username, password):
    """
        Makes HTTP GET request to a URL using the supplied username and password credentials.
    :rtype : a 3-tuple of the target URL, the data of the response, and an error code
    :param realm:
    :param uri:
    :param hostname:
    :param protocol:
    :param port:
    :param username:
    :param password:
    """

    if port == '':
        server = protocol + "://" + hostname
    else:
        server = protocol + "://" + hostname + ":" + port
    passMgr = urllib2.HTTPPasswordMgr()
    passMgr.add_password(realm, server, username, password)
    authhandler = urllib2.HTTPBasicAuthHandler(passMgr)
    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)
    url = "%s/%s" % (server, uri)

    try:
        f = urllib2.urlopen(url)
        statusCode = f.getcode()
        data = f.read()
        result = (url, data, statusCode)
    except urllib2.HTTPError, e:
        print 'The server (%s) couldn\'t fulfill the request.' % server
        print 'Error code: ', e.code
        result = (url, None, e.code)
    except urllib2.URLError, e:
        print 'We failed to reach the server (%s).' % server
        print 'Reason: ', e.reason
        result = (url, None, e.reason)

    return result


def postxml(realm, uri, hostname, protocol, port, username, password, payload, requestType):

    if port == '':
        server = protocol + "://" + hostname
    else:
        server = protocol + "://" + hostname + ":" + port
    passMgr = urllib2.HTTPPasswordMgr()
    passMgr.add_password(realm, server, username, password)
    authhandler = urllib2.HTTPBasicAuthHandler(passMgr)
    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)
    url = "%s/%s" % (server, uri)

    elapsedtime = time.time()
    request = urllib2.Request(url, payload, {'Content-Type': 'application/xml'})
    # default method for urllib2 with payload is POST
    if requestType == 'PUT': request.get_method = lambda: 'PUT'

    try:
        f = urllib2.urlopen(request)
        statusCode = f.getcode()
        data = f.read()
        info = f.info()
        # if a POST, the Location element contains the new CSID
        if info.getheader('Location'):
            csid = re.search(uri + '/(.*)', info.getheader('Location'))
            csid = csid.group(1)
        else:
            csid = ''
        return (url, data, csid, time.time() - elapsedtime)
    except urllib2.HTTPError, e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        return (url, None, e.code, time.time() - elapsedtime)
    except urllib2.URLError, e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
        return (url, None, e.reason, time.time() - elapsedtime)
    except:
        raise


class connection:
    def __init__(self, realm, uri, hostname, protocol, port, username, password, payload, requesttype):
        self.realm = realm
        self.uri = uri
        self.hostname = hostname
        self.protocol = protocol
        self.port = port
        self.username = username
        self.password = password
        self.payload = payload
        self.requesttype = requesttype

    @classmethod
    def create_connection(cls, config, user):
        """
            Factory method for creating a new connection.
        :param user:
        :param config:
        :return:
        """
        realm = getConfigOptionWithSection(config, CONFIGSECTION_SERVICES_CONNECT, CSPACE_REALM_PROPERTY)
        hostname = getConfigOptionWithSection(config, CONFIGSECTION_SERVICES_CONNECT, CSPACE_HOSTNAME_PROPERTY)
        protocol = getConfigOptionWithSection(config, CONFIGSECTION_SERVICES_CONNECT, CSPACE_PROTOCOL_PROPERTY)
        port = getConfigOptionWithSection(config, CONFIGSECTION_SERVICES_CONNECT, CSPACE_PORT_PROPERTY)
        return connection(realm, None, hostname, protocol, port, user.username, user.cspace_password, None, None
        )

    def make_get_request(self, uri=None):
        """

        :param uri:
        :return:
        """
        requestUri = uri
        if requestUri is None:
            requestUri = self.uri

        result = make_get_request(self.realm, requestUri, self.hostname, self.protocol, self.port,
                                  self.username, self.password)

        return result


    def postxml(self, uri=None, payload=None, requesttype=None):
        requestUri = uri
        if requestUri is None:
            requestUri = self.uri

        requestPayload = payload
        if requestPayload is None:
            requestPayload = self.payload

        requestRequesttype = requesttype
        if requestRequesttype is None:
            requestRequesttype = self.requesttype

        result = postxml(self.realm, requestUri, self.hostname, self.protocol, self.port,
                         self.username, self.password, requestPayload, requestRequesttype)

        return result

# https://djangosnippets.org/snippets/243/
import base64

from django.http import HttpResponse
from django.contrib.auth import authenticate, login

#############################################################################
#
def view_or_basicauth(view, request, test_func, realm = "", *args, **kwargs):
    """
    This is a helper function used by both 'logged_in_or_basicauth' and
    'has_perm_or_basicauth' that does the nitty of determining if they
    are already logged in or if they have provided proper http-authorization
    and returning the view if all goes well, otherwise responding with a 401.
    """
    if test_func(request.user):
        # Already logged in, just return the view.
        #
        return view(request, *args, **kwargs)

    # They are not logged in. See if they provided login credentials
    #
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: We are only support basic authentication for now.
            #
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                user = authenticate(username=uname, password=passwd)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        return view(request, *args, **kwargs)

    # Either they did not provide an authorization header or
    # something in the authorization attempt failed. Send a 401
    # back to them to ask them to authenticate.
    #
    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return response

#############################################################################
#
def logged_in_or_basicauth(realm = ""):
    """
    A simple decorator that requires a user to be logged in. If they are not
    logged in the request is examined for a 'authorization' header.

    If the header is present it is tested for basic authentication and
    the user is logged in with the provided credentials.

    If the header is not present a http 401 is sent back to the
    requestor to provide credentials.

    The purpose of this is that in several django projects I have needed
    several specific views that need to support basic authentication, yet the
    web site as a whole used django's provided authentication.

    The uses for this are for urls that are access programmatically such as
    by rss feed readers, yet the view requires a user to be logged in. Many rss
    readers support supplying the authentication credentials via http basic
    auth (and they do NOT support a redirect to a form where they post a
    username/password.)

    Use is simple:

    @logged_in_or_basicauth
    def your_view:
        ...

    You can provide the name of the realm to ask for authentication within.
    """
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(func, request,
                                     lambda u: u.is_authenticated(),
                                     realm, *args, **kwargs)
        return wrapper
    return view_decorator

#############################################################################
#
def has_perm_or_basicauth(perm, realm = ""):
    """
    This is similar to the above decorator 'logged_in_or_basicauth'
    except that it requires the logged in user to have a specific
    permission.

    Use:

    @logged_in_or_basicauth('asforums.view_forumcollection')
    def your_view:
        ...

    """
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(func, request,
                                     lambda u: u.has_perm(perm),
                                     realm, *args, **kwargs)
        return wrapper
    return view_decorator
