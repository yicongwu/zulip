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
    do_remove_default_stream
from zerver.lib.response import json_success, json_error, json_response
from zerver.lib.validator import check_string, check_list, check_dict, \
    check_bool, check_variable_type
from zerver.models import UserProfile, Stream, Subscription, Group, \
    Recipient, get_recipient, get_stream, bulk_get_streams, \
    bulk_get_recipients, valid_stream_name, get_active_user_dicts_in_realm

from collections import defaultdict
import ujson
from six.moves import urllib

import six
from six import text_type


def create_group(request, name, owner_id):
    owner = UserProfile.objects.get(id=owner_id)
    #create group
    group = Group.create(name, owner)
    return json_success()

def delete_group(request, group_id):
    group = Group.objects.get(id=group_id)
    recipient = Recipient.objects.get(type_id=group.id, type=Recipient.GROUP)
    #delete related subscription
    Subscription.objects.filter(recipient=recipient).delete()
    #delete recipient
    recipient.delete()
    #delete group
    group.delete()
    return json_success()

def all_groups(request):
    return json_success({'group_id':Group.objects.all().values("id"),
                            'group_name':Group.objects.all().values("name")
    })

def all_users(request):
    return json_success({'UserProfile':UserProfile.objects.all().values("id")})

def all_members(request, group_id):
    recipient = Recipient.objects.get(type_id=group_id, type=Recipient.GROUP)
    members = Subscription.objects.filter(recipient=recipient)
    return json_success({'members':members.values("user_profile")})
    
def change_group_name(request, group_id, newname):
    group=Group.objects.filter(id=group_id)
    group.update(name=newname)
    return json_success()

def delete_group_member(request, group_id, member_id):
    member = UserProfile.objects.get(id=member_id)
    recipient = Recipient.objects.get(type_id=group_id, type=Recipient.GROUP)
    Subscription.objects.filter(user_profile=member, recipient=recipient).delete()
    return json_success()

def add_group_member(request, group_id, user_id):
    user = UserProfile.objects.get(id=user_id)
    recipient = Recipient.objects.get(type_id=group_id, type=Recipient.GROUP)
    subscription = Subscription(user_profile=user, recipient=recipient)
    subscription.save()
    return json_success()