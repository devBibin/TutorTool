# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from models import *
#from utils import *

import requests
import json
import re

import os

GATEWAY_URL = "http://localhost:8000"
FILE_SYSTEM_URL = "http://localhost:8001"
USER_URL = "http://localhost:8002"

#==============================================================================
#==========================TEMP FUNCTIONS======================================
def index(request):
    print user_auth(request)
    return render(request, 'gatewayapp/base.html')

def login(request):
    response = send_request(request, USER_URL)
    return HttpResponse(response.content)

def logout(request):
    response = send_request(request, USER_URL)
    return HttpResponse(response.content)
#==============================================================================


#==============================================================================
#=======================CREATE REPOSITORY======================================
def create_repo(request):
    return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")
#==============================================================================


#==============================================================================
#===============================FOLDER API=====================================
def get_folder(request, folder_id=None):
    return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")

def create_folder(request, parent_id=None):
    return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")

def remove_folder(request, id):
    return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")
#==============================================================================
#==============================================================================



#==============================================================================
#=================================FILE API=====================================
def upload_file(request, parent_id=None):
    return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")


def download_file(request, id):
    return HttpResponseRedirect(FILE_SYSTEM_URL + request.path)


def remove_file(request, id):
    return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")
#==============================================================================
#==============================================================================



#==============================================================================
#==============================QUESTIONS API===================================
def add_question(request):
    if (request.method == "GET"):
        return render(request, 'gatewayapp/question.html')
    elif (request.method == "POST"):
        return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")

def remove_question(request, id):
    return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")

def get_question(request, question_id):
    return fs_system_navigation(request, "gatewayapp/question.html", "question")
#==============================================================================


#==============================================================================
#==============================TEST API========================================
def add_test(request):
    if (request.method == "GET"):
        return render(request, 'gatewayapp/test.html')
    elif (request.method == "POST"):
        return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")


def remove_test(request, id):
    return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")


def get_test(request, test_id):
    return fs_system_navigation(request, 'gatewayapp/test.html', "test")


def search_for_test(request, test_id):
    return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")


def submit_test(request, test_id):
    return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")


def add_question_to_test(request, question_id, test_id):
    return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")  
#==============================================================================



#==============================================================================
#===========================TRANSFERING OBJECTS API============================
def transfer_object(request, object_type, object_id):
    return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")


def submit_transfer(request, parent_id = None):
    return fs_system_navigation(request, "gatewayapp/file_system.html", "fs")
#==============================================================================


#===============================================================================
#===========================SERVICE FUNCTIONS===================================
def set_user_id(request):
    try:
        user = request.user.pk
    except:
        return False
    if (request.method == "POST"):
        request_data = request.POST.copy()
        request_files = request.FILES
        request_data["user"] = user
    elif (request.method == "GET"):
        request_data = request.GET.copy()
        request_files = None
        request_data["user"] = user
    return request_data, request_files


def send_request(request, system):
    path = str(request.path)
    data, files = set_user_id(request)
    if (data):
        if (request.method == "POST"):
            response = requests.post(system + path, data = data, files = files)
        elif (request.method == "GET"):
            response = requests.get(system + path, params = data)
        else:
            return False
    else:
        return False
    return response


def get_dict_by_name(data, name):
    if (name == "fs"):
        return {
         "dirs" : data["dirs"],
         "files" : data["files"],
         "tests" : data["tests"],
         "questions": data["questions"],
         "master": data["master"],
         "mode": data["mode"],
         "title": data["title"],
         "test_id": data["test_id"],
        }
    elif (name == "question"):
        return {
         "question": data["question"],
         "questionchoices" : data["questionchoices"],
        }
    elif (name == "test"):
        return {
         "test" : data["test"],
         "questions": data["questions"]
        }


def fs_system_navigation(request, template_source, dict_name):
    response = send_request(request, FILE_SYSTEM_URL)
    if (response.status_code == 200):
        if (dict_name == "fs" and response.content.find("Parent for redirect") != -1):
            s = response.content
            parent = s[s.find("[")+len("]"):s.rfind("]")]
            try:
                parent = int(parent)
                return HttpResponseRedirect(GATEWAY_URL + "/file-system/"+str(parent)+"/")
            except:
                parent = False
                return HttpResponseRedirect(GATEWAY_URL + "/file-system/")
        else:
            data = json.loads(response.content)
        return render(request, template_source, get_dict_by_name(data, dict_name))
    else:
        return HttpResponse("Error")  