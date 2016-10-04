#This is the APIs for OAuth2.0 for WeChart written by yicong
from __future__ import absolute_import
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from zerver.lib.response import json_success, json_error, json_response
from zerver.lib.actions import do_create_user
from zerver.models import UserProfile, Association, get_unique_open_realm
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, get_backends
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse, HttpRequest
from django.utils.timezone import now

from six.moves import urllib, zip_longest, zip, range
from django.middleware.csrf import get_token
import hashlib
import hmac
import logging
import requests
import time
import ujson

import simplejson
import pdb

def baidu_oauth2_csrf(request, value):
    # type: (HttpRequest, str) -> HttpResponse
    return hmac.new(get_token(request).encode('utf-8'), value, hashlib.sha256).hexdigest()

#redirect user to the third party
def start_baidu_oauth2(request):
    url = 'http://openapi.baidu.com/oauth/2.0/authorize?'
   # cur_time = str(int(time.time()))
   # csrf_state = '{}:{}'.format(
   #     cur_time,
   #     baidu_oauth2_csrf(request, cur_time),
   # )
    prams = {
        'response_type': 'code',
        'client_id': settings.BAIDU_OAUTH_CLIENT_ID,
        'redirect_uri': ''.join((
            settings.EXTERNAL_URI_SCHEME,#http://  or https://
            request.get_host(),#localhost:9991/
            reverse('zerver.views.baidu.finish_baidu_oauth2'),
        )),
        'scope': 'basic', 
        'display':'popup',
       # 'state': csrf_state,
    }
    return redirect(url + urllib.parse.urlencode(prams))

# Workaround to support the Python-requests 1.0 transition of .json
# from a property to a function
requests_json_is_function = callable(requests.Response.json)
def extract_json_response(resp):
    # type: (HttpResponse) -> Dict[str, Any]
    if requests_json_is_function:
        return resp.json()
    else:
        return resp.json

def finish_baidu_oauth2(request):
    error = request.GET.get('error')
    if error == 'access_denied':
        return redirect('/')
    elif error is not None:
        logging.warning('Error from baidu oauth2 login %r', request.GET)
        return HttpResponse(status=400)

   # value, hmac_value = request.GET.get('state').split(':')
   # if hmac_value != google_oauth2_csrf(request, value):
   #     logging.warning('baidu oauth2 CSRF error')
   #     return HttpResponse(status=400)
    code = request.GET.get('code')
    ask_token_uri = 'https://openapi.baidu.com/oauth/2.0/token?grant_type=authorization_code&code='+code+'&client_id='+\
                    settings.BAIDU_OAUTH_CLIENT_ID+'&client_secret='+settings.BAIDU_OAUTH_SECRET+\
                    '&redirect_uri=http://localhost:9991/login/baidu/complete/'
    resp = requests.get(
        ask_token_uri
    )
    #check whether get right access token
    #if resp.status_code == 400:
     #   logging.warning('User error converting baidu oauth2 login to token')
       # return HttpResponse(status=400)
    #elif resp.status_code != 200:
      #  raise Exception('Could not convert baidu oauth2 code to access_token')
    try:
        body = extract_json_response(resp)
        access_token = body['access_token']
    except:
        raise Exception('Could not get baidu acess_token.')
    ask_info_uri = 'https://openapi.baidu.com/rest/2.0/passport/users/getLoggedInUser?access_token='+access_token
    resp_info = requests.post(
        ask_info_uri
    )
    try:
        body = extract_json_response(resp_info)
        uid = body['uid']
        uname= body['uname']
    except:
        raise Exception('Could not get baidu uid.')
    email = Association.get_email_by_account('baidu', uid)
    if email == None :
        #reigister
        full_name = uname
        short_name = '----'
        password = None
        fake_email = uid + '@baidu.com'
        Association.create_association(fake_email,'baidu',uid)
        realm = get_unique_open_realm()
        user_profile = do_create_user(fake_email, password, realm, full_name, short_name)
        user_profile = authenticate(username=fake_email, use_dummy_backend=True) # may be non-meaningful
        login(request, user_profile)
    else:
        user_profile = authenticate(username=email, use_dummy_backend=True)
        login(request, user_profile)
    #if request.user.is_authenticated():
        #return json_success({'email':request.user.email, 'baiduid':uid})
   # else :
       # return json_error("user is not authenticated!")
    return HttpResponseRedirect("%s%s" % (settings.EXTERNAL_URI_SCHEME,
                                          request.get_host()))
   
   