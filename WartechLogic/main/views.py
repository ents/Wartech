# coding=utf-8
import random
import string
from django.http import HttpResponse, Http404
import json
from django.template import RequestContext
from django.shortcuts import render_to_response
from models import *


def JsonResponse(request, data):
    mimetype = 'text/plain'
    if 'HTTP_ACCEPT_ENCODING' in request.META.keys():
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
    response = HttpResponse(json.dumps(data), content_type=mimetype)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "86400"
    response["x-test"] = "super secret header"
    if request.method == "OPTIONS":
        response["Access-Control-Allow-Headers"] = "origin, content-type, x-requested-with, accept, authorization"
    return response


def home(request):
    return render_to_response('home.html', {}, context_instance=RequestContext(request))


def dummy(request):
    data = {'Artem': 'Kurtem'}
    return JsonResponse(request, data)


def init(request):
    session_key = ''.join(random.choice(string.letters) for _ in xrange(128))
    session = Session()
    session.session_id = session_key
    session.save()
    data = {'session_id': session_key}
    return JsonResponse(request, data)


def get_request_value(request, key):
    if request.method == "GET":
        return request.GET[key]
    else:
        return request.POST[key]


def get_session(request):
    session_id = get_request_value(request, "session_id")
    session = Session.objects.get(session_id=session_id)
    if not session:
        raise Exception("session not found")
    return session


def get_all_users(request):
    session = get_session(request)
    user = session.user
    if not user:
        raise Exception("user not found")
    users = User.objects.filter(is_online=True).all()
    data = [{'name': user.name, 'available_for_fight': user.id != session.user.id} for user in users]
    return JsonResponse(request, data)


def request_fight(request):
    data = {
        'granted': True,
        'arena': {
            'width': 20,
            'height': 20,
            'cells': [
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            ],
        },
        'fight_replay': {},
    }
    return JsonResponse(request, data)


def get_all_modules(request):
    data = [
        {
            'slot': 'sensor',
            'modules': [
                'optic',
                'sound',
                'wifi'
            ]
        },
        {
            'slot': 'processor',
            'modules': [
                'Pentium I',
                'Pentium II',
                'Pentium III',
                'Pentium IV'
            ]
        }
    ]
    return JsonResponse(request, data)


def get_user_robot(request):
    data = {
        'hull_name': 'monster',
        'hull_slots': [
            {
                'id': 1,
                'slot': 'sensor',
                'module': 'eye',
            },
            {
                'id': 32,
                'slot': 'sensor',
                'module': 'eye',
            },
            {
                'id': 2,
                'slot': 'motion',
                'module': 'legs',
                'params': {
                    'count': 3,
                },
            },
            {
                'id': 3,
                'slot': 'energy',
                'module': 'battery',
                'params': {
                    'energy': 87,
                    'capacity': 100
                },
            },
            {
                'id': 4,
                'slot': 'processor',
                'module': 'Pentium III',
                'params': {
                    'overheat': 12,
                },
            }
        ],
    }
    return JsonResponse(request, data)


def get_user_modules(request):
    data = [
        {
            'id': 1,
            'slot': 'sensor',
            'module': 'optic',
            'equipped': False,
        },
        {
            'id': 3,
            'slot': 'power',
            'module': 'Battery 10KJ',
            'equipped': True,
        },
        {
            'id': 4,
            'slot': 'power',
            'module': 'Battery 10KJ',
            'equipped': False,
        },
        {
            'id': 47,
            'slot': 'processor',
            'module': 'Pentium II',
            'equipped': False,
        }
    ]
    return JsonResponse(request, data)


def set_module_to_slot(request):
    data = {
        'ok': True,
        'unequipped_module': 4, # -1 if no module was unequipped
        'error_reason': '',
    }
    return JsonResponse(request, data)


def create_new_user(request):
    data = {
        'id': 11023,
        'session_id': '$fFDf32sd$@$@#$sdf3424fsd3==43223%@@!d', #must be added to cookies
        'user_name': 'RJ122302',
        'serial_number': '00203-22-108', #unique text id, which cannot be changed by user
    }
    return JsonResponse(request, data)


def login(request):
    data = {
        'granted': False,
        'error_message': 3, # e.g., "3" is localization key, which corresponds to 'invalid password'
    }
    return JsonResponse(request, data)


def logout(request):
    data = {}
    return JsonResponse(request, data)
