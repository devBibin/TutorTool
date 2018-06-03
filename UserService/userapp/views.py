# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User


def login(request):
    username = "foo"
    password = "bar"
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return HttpResponse("Success")
    else:
        return HttpResponse("Fail")


def logout(request):
    auth.logout(request)
    return HttpResponse("Hello")
