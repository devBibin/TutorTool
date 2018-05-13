# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse

def index(request):
    return render(request, 'file_conductor_app/base.html')
# Create your views here.
