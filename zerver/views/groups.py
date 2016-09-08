#This is the APIs for class GROUP written by yicong for test
from __future__ import absolute_import
from typing import Any, Optional, Tuple, List, Set, Iterable, Mapping, Callable

from django.utils.translation import ugettext as _
from django.conf import settings
from django.db import transaction
from django.http import HttpRequest, HttpResponse

from zerver.lib.request import JsonableError, REQ, has_request_variables
from zerver.decorator import authenticated_json_post_view, \
    authenticated_json_view, \
    get_user_profile_by_email, require_realm_admin
from zerver.lib.actions import bulk_remove_subscriptions, \
    do_change_subscription_property, internal_prep_message, \
    create_stream_if_needed, gather_subscriptions, subscribed_to_stream, \
    bulk_add_subscriptions, do_send_messages, get_subscriber_emails, do_rename_stream, \
    do_deactivate_stream, do_make_stream_public, do_add_default_stream, \
    do_change_stream_description, do_get_streams, do_make_stream_private, \
    do_remove_default_stream, do_create_user
from zerver.lib.response import json_success, json_error, json_response
from zerver.lib.validator import check_string, check_list, check_dict, \
    check_bool, check_variable_type
from zerver.models import UserProfile, Stream, Subscription, Group, UserMessage,\
    Recipient, get_recipient, get_stream, bulk_get_streams, Message, Client, \
    bulk_get_recipients, valid_stream_name, get_active_user_dicts_in_realm, \
    email_to_username, Realm

from collections import defaultdict
import ujson
from six.moves import urllib
import simplejson
import six
from six import text_type
from django.views.decorators.csrf import csrf_exempt   
from zerver.views.messages import send_message_backend, get_old_messages_backend
from zerver.lib.actions import check_send_message
from django.contrib.auth.decorators import login_required 

import pdb;

@csrf_exempt 
def dispatch_group(request):
    if request.method=='GET':
        return all_groups(request)
    elif request.method=='POST':
        return create_group(request)
    elif request.method=='DELETE':
        return delete_group(request)
    elif request.method=='PATCH':
        return change_group_name(request)
    return json_error()

@csrf_exempt
def dispatch_member(request):
    if request.method=='POST':
        return add_group_member(request)
    elif request.method=='DELETE':
        return delete_group_member(request)
    return json_error()

@login_required   
def create_group(request):
    json_data = simplejson.loads(request.body)
    name = json_data['name']
    #owner_id = json_data['owner_id']
    #owner = UserProfile.objects.get(id=owner_id)
    owner = request.user
    #whether the group has been created
    if (Group.objects.filter(name=name, owner=owner).count()!=0):
        return json_error("The group exists !")
    #create group
    group = Group.create(name, owner)
    return json_success({'group_id':Group.objects.get(name=name, owner_id=owner.id).id,
                        'name':Group.objects.get(name=name, owner_id=owner.id).name
    })

@login_required
def delete_group(request):
    json_data = simplejson.loads(request.body)
    #group_id = json_data['group_id']
    name = json_data['name']
    #owner_id = json_data['owner_id']
    owner_id = request.user.id
    try:
        group = Group.objects.get(name=name, owner_id=owner_id)
    except:
        return json_error("You do not have this group")
    recipient = Recipient.objects.get(type_id=group.id, type=Recipient.GROUP)
    #delete related subscription
    Subscription.objects.filter(recipient=recipient).delete()
    #delete recipient
    recipient.delete()
    #delete group
    group.delete()
    return json_success()
        
@login_required
def change_group_name(request):
    try:
        json_data = simplejson.loads(request.body)
        group_id = json_data['group_id']
        newname = json_data['newname']
        group = Group.objects.get(id=group_id)
        #check ownership of the group
        if (request.user.id != group.owner.id):
            return json_error("You are not the owner of this group")
        #check newname availablility
        if (Group.objects.filter(name=newname, owner=group.owner).count()!=0):
            return json_error("Group name has been used!")
        group.name = newname
        group.save()
    except:
        return json_error("No such group!")
    return json_success()

def all_groups(request):
    return json_success({'group_id':Group.objects.all().values("id"),
                        'name':Group.objects.all().values("name"),
                        'owner':Group.objects.all().values("owner")
    })

def all_users(request):
    return json_success({'UserProfile':[UserProfile.objects.all().values("id"),UserProfile.objects.all().values("full_name")]})

@login_required
def all_members(request, group_id):
    try:
        recipient = Recipient.objects.get(type_id=group_id, type=Recipient.GROUP)
        members = Subscription.objects.filter(recipient=recipient)
    except:
        return json_error("No such group.")
    #check membership
    if (Subscription.objects.filter(recipient=recipient, user_profile=request.user).count()==0):
        return json_error("You are not in the group")
    return json_success({'members':members.values("user_profile")})

@login_required
def delete_group_member(request):
    #check ownership of the group
    if (request.user.id != group.owner.id):
        return json_error("You are not the owner of this group")
    json_data = simplejson.loads(request.body)
    group_id = json_data['group_id']
    member_id = json_data['user_id']
    try:
        member = UserProfile.objects.get(id=member_id)
        recipient = Recipient.objects.get(type_id=group_id, type=Recipient.GROUP)
        Subscription.objects.filter(user_profile=member, recipient=recipient).delete()
    except:
        return json_error("No such group or member!")
    return json_success()

@login_required
def add_group_member(request):
    #check ownership of the group
    if (request.user.id != group.owner.id):
        return json_error("You are not the owner of this group")
    json_data = simplejson.loads(request.body)
    group_id = json_data['group_id']
    user_id = json_data['user_id']
    try:
        user = UserProfile.objects.get(id=user_id)
        recipient = Recipient.objects.get(type_id=group_id, type=Recipient.GROUP)
        subscription = Subscription(user_profile=user, recipient=recipient)
        subscription.save()
    except:
        return json_error("No such group or user!")
    return json_success()

@login_required
def get_a_user_profile(request, user_id):
    try:
        user_profile = UserProfile.objects.get(id=user_id)
    except:
        return json_error("No such user.")

    return json_success({'user_profile':user_profile.realm.name})

@csrf_exempt
@login_required
def send_message_to_memebers(request):
    if request.method != 'POST' :
        return json_error("Wrong Method.")
    json_data = simplejson.loads(request.body)
    #user_id = json_data['user_id']
    message_type_name = json_data['message_type_name']
    recipient_id = json_data['recipient_id']
    message_content = json_data['message_content']
    subject_name = json_data['subject_name']
    try:
        #user_profile = UserProfile.objects.get(id=user_id)
        if message_type_name == 'group':
            message_to = Recipient.objects.get(type_id=recipient_id, type=Recipient.GROUP)
            #check membership
            if (Subscription.objects.filter(recipient=message_to, user_profile=request.user).count()==0):
                return json_error("You are not the member of the group!")
        client = Client.objects.get(id=3)
    except:
        return json_error("No such user or group")
        #skip send_message_backend in order to avoid data structure inconsistence
    result_id = check_send_message(user_profile, client, message_type_name, message_to, subject_name, message_content)
    return json_success({"id":result_id})

def get_group_messages(request, group_id):
    recipient = Recipient.objects.get(type_id=group_id, type=Recipient.GROUP)
    return json_success({'messages':Message.objects.filter(recipient=recipient).values("content")})

@login_required
def get_client_name(request):
    return json_success({'client_id':Client.objects.all().values("id"), 'client_name':Client.objects.all().values("name")})

# get num_before messages before anchor and num_after messages after anchor
@login_required
def get_user_messages(request, user_id):
    user_profile=request.user
    result = get_old_messages_backend(request, user_profile)
    return result

def get_one_message(message_id):
    try:
        message = Message.objects.get(id=message_id)
    except:
        return None
    return message

#delete group messages
@csrf_exempt
@login_required
def delete_group_message(request):
    if request.method != 'DELETE':
        return json_error("Wrong method")
    json_data = simplejson.loads(request.body)
    group_id = json_data['group_id']
    #check ownership of the group
    group = Group.objects.get(id=group_id)
    if (request.user.id != group.owner.id):
        return json_error("You are not the owner of this group")
    #user_id = json_date['user_id']
    try:
        #if user_id > 0:
            #user_profile = UserProfile.objects.get(id=user_id)
        recipient = Recipient.objects.get(type_id=group_id, type=Recipient.GROUP)
    except:
        return json_error("No such group or user")
    messages = Message.objects.filter(recipient=recipient)
    #messages_ids = messages.values('id')
    user_messages = UserMessage.objects.filter(message__in = messages)
    #delete related messages in UserMessage
    user_messages.delete()
    #delete related messages in Message
    messages.delete()
    return json_response(res_type="success", msg="All group messages are deleted!")

#informally create/delete user in order to test email/pass login in dev environment
@csrf_exempt
def create_user_dev(request):
    if request.method != 'POST':
        return json_error("Wrong method")
    json_data = simplejson.loads(request.body)
    email = json_data['email']
    password = json_data['password']
    realm = Realm.objects.get(name='Tijee_test')
    full_name = json_data['full_name']
    short_name = email_to_username(email)
    if (UserProfile.objects.filter(email=email).count()!=0):
        return json_error("The email has been used!") 
    user_profile = do_create_user(email, password, realm, full_name, short_name)
    return json_success({'user_id':user_profile.id, 'user_name':user_profile.full_name, 'user_email':user_profile.email})

@csrf_exempt
def delete_user_dev(request):
    if request.method != 'DELETE':
        return json_error("Wrong method")
    json_data = simplejson.loads(request.body)
    user_id = json_data['user_id']
    
    name = UserProfile.objects.get(id=user_id).full_name
    UserProfile.objects.filter(id=user_id).delete()
    return json_success({'name':name})