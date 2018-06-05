# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from models import *
from utils import *

import requests
import json
import re

import os

import logging
log = logging.getLogger(__name__)

GATEWAY_URL = "http://localhost:8000"
FILE_SYSTEM_URL = "http://localhost:8001"
USER_URL = "http://localhost:8002"
LESSON_URL = "http://localhost:8003"


def index(request):
    return render(request, 'gatewayapp/base.html')


#==============================================================================
#==============================================================================       
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==========================LESSON FUNCTIONS====================================
def add_lesson(request, student_id):
    data, files = get_request_data(request)
    verify_info = verify(request)
    if (without_error(verify_info)):
          
        if (check_if_in_group(verify_info["user"]["groups"], "Teacher")):
            if (has_relation(verify_info["user"]["id"], student_id)):
                response = safe_send_request(LESSON_URL + "/lesson/add/"+str(verify_info["user"]["id"])+"/for/"+str(student_id)+"/", 
                    {"info" : "helloworld"},
                    "LessonService",
                    "POST")
                if (not without_error(response)):
                    return HttpResponse(response["service_message"])
                elif (response.status_code == 200):
                    return HttpResponse(response.content)
                elif (response.status_code == 400):
                    return HttpResponse(response.content)
                else:
                    return HttpResponse("Unknown error")
            else:
                return HttpResponse("No active relation between student and teacher")
        else:
            return HttpResponse("Lessons can be added only by teachers")
    else:
        return HttpResponse(verify_info["service_message"])  


def get_lessons(request, user_id = None):
    verify_info = verify(request)
    if (without_error(verify_info)):
        
        
        if (check_if_in_group(verify_info["user"]["groups"], "Teacher")):
            if (user_id == None):
                response = safe_send_request(LESSON_URL + "/lesson/get/"+str(verify_info["user"]["id"])+"/0/", 
                    {},
                    "LessonService",
                    "POST")
            else:
                response = safe_send_request(LESSON_URL + "/lesson/get/"+str(verify_info["user"]["id"])+"/"+str(user_id)+"/",
                    {},
                    "LessonService",
                    "POST") 
        elif ((check_if_in_group(verify_info["user"]["groups"], "Student"))):
            if (user_id == None):
                response = safe_send_request(LESSON_URL + "/lesson/get/0/"+str(verify_info["user"]["id"])+"/", 
                    {},
                    "LessonService",
                    "POST")
            else:
                response = safe_send_request(LESSON_URL + "/lesson/get/"+str(user_id)+"/"+str(verify_info["user"]["id"])+"/",
                    {},
                    "LessonService",
                    "POST")
        else:
            return HttpResponse("Unknown user")                           
        
        if (not without_error(response)):
            return HttpResponse(response["service_message"])
        elif (response.status_code == 200):
            return HttpResponse(response.content)
        else:
            return HttpResponse("Unknown error")
    else:
        return HttpResponse(verify_info["service_message"])  


def add_homework_item(request, lesson_id, object_type, object_id):
    data, files = get_request_data(request)
    verify_info = verify(request)
    if (without_error(verify_info)):
        
        response = safe_send_request(LESSON_URL + "/lesson/"+object_type+"/"+str(object_id)+"/to/"+str(lesson_id)+"/", 
            {"user" : verify_info["user"]["id"]},
            "LessonService",
            "POST")
        
        if (not without_error(response)):
            return HttpResponse(response["service_message"])
        elif (response.status_code == 200):
            return HttpResponse(response.content)
        elif (response.status_code == 400):
            return HttpResponse("Forbidden")
        else:
            return HttpResponse("Unknown error")
    else:
        return HttpResponse(verify_info["service_message"])
#==============================================================================
#==============================================================================       
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==========================USER FUNCTIONS======================================
def register(request):
    data, files = get_request_data(request)
    data = {"username" : "Master", "password" : "qaz", "group" : "Teacher"}
    
    # Send data for register
    response = safe_send_request(USER_URL + "/user/register/", 
        data,
        "UserService",
        "POST")    
    if (not without_error(response)):
        return HttpResponse(response["service_message"])
    elif (response.status_code == 200):
        if (data["group"] == "Teacher"):
            # Creating repository for teacher
            response = create_repo(request, response.content)
            if (not without_error(response)):
                return HttpResponse(response["service_message"])
        # Login in case of success of register
        return login(request)
    elif (response.status_code == 400):
        return HttpResponse("User exists")


def logout(request):
    response = HttpResponse("Logged out")
    response.set_cookie(key="auth_token", value="Logged out")
    return response


def login(request):
    data, files = get_request_data(request)
    data = {"username" : "Student", "password" : "qaz"}
    response = safe_send_request(USER_URL + "/user/login/", 
        data,
        "UserService",
        "POST")
    
    if (not without_error(response)):
        return HttpResponse(response["service_message"])
    elif (response.status_code == 200):
        data = json.loads(response.content)
        response = render(request, 'gatewayapp/base.html', {"user" : data["user"]["username"]})
        response.set_cookie(key='auth_token', value=data["token"])
        return response
    elif (response.status_code == 400):
        print response.content
        return HttpResponse("Bad credentials")
    else:
        return HttpResponse("Unknown error")


def refresh(request):
    response = safe_send_request(USER_URL + "/user/refresh/", 
        {'token' : request.COOKIES.get('auth_token')},
        "UserService",
        "POST")
    
    if (not without_error(response)):
        return response
    elif (response.status_code == 200):
        return response.content
    elif (response.status_code == 400):
        return {"service_message" : "Login required"}
    else:
        return {"service_message" : "Unknown error"}


def verify(request):
    response = safe_send_request(USER_URL + "/user/verify/", 
        {'token' : request.COOKIES.get('auth_token')},
        "UserService",
        "POST")
    
    if (not without_error(response)):
        return response
    elif (response.status_code == 200):
        return json.loads(response.content)
    elif (response.status_code == 400):
        return {"service_message" : "Login required"}
    else:
        return {"service_message" : "Unknown error"}


def subscribe(request, teacher_id):
    verify_info = verify(request)
    if (without_error(verify_info)):
        
        response = safe_send_request(USER_URL + "/user/subscribe/"+str(verify_info["user"]["id"])+"/to/"+str(teacher_id)+"/", 
            {},
            "UserService",
            "POST")
        if (without_error(response)):
            return HttpResponse(response)
        else:
            return HttpResponse(response["service_message"])
    else:
        return HttpResponse(verify_info["service_message"])       


def confirm(request, student_id):
    verify_info = verify(request)
    if (without_error(verify_info)):
        
        response = safe_send_request(USER_URL + "/user/"+str(verify_info["user"]["id"])+"/confirm/"+str(student_id)+"/", 
            {},
            "UserService",
            "POST")
        if (without_error(response)):
            return HttpResponse(response)
        else:
            return HttpResponse(response["service_message"])
    else:
        return HttpResponse(verify_info["service_message"])       


def decline(request, student_id):
    verify_info = verify(request)
    if (without_error(verify_info)):
        
        response = safe_send_request(USER_URL + "/user/"+str(verify_info["user"]["id"])+"/decline/"+str(student_id)+"/", 
            {},
            "UserService",
            "POST")
        if (without_error(response)):
            return HttpResponse(response)
        else:
            return HttpResponse(response["service_message"])
    else:
        return HttpResponse(verify_info["service_message"])  


def get_info(request, user_id):
    verify_info = verify(request)    
    if (without_error(verify_info)):
        response = safe_send_request(USER_URL + "/user/info/"+str(user_id)+"/", 
            {},
            "UserService",
            "GET")
        if (without_error(response)):
            return HttpResponse(response.content)
        else:
            return HttpResponse(response["service_message"]) 
    else:
        return HttpResponse(verify_info["service_message"])


def has_relation(teacher, student):
    response = safe_send_request(USER_URL + "/user/"+str(teacher)+"/relation/"+str(student)+"/", 
        {},
        "UserService",
        "POST")
    if response.status_code == 200:
        print "OK"
        return True
    else:
        print "Not ok"
        return False    
#==============================================================================


#==============================================================================
#=======================CREATE REPOSITORY======================================
def create_repo(request, user_id):
    response = safe_send_request(FILE_SYSTEM_URL + "/file-system/create/", 
        {"user" : user_id},
        "FileSystem",
        "POST")
    if (without_error(response)):
        return HttpResponse("Repository was created")
    else:
        return response
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
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#===========================SERVICE FUNCTIONS==================================
# Check if in respose json with service message
def without_error(data):
    try:
        log.info("Error is " + str(data["service_message"]))
        return False
    except:
        return True


def check_if_in_group(data, group):
    for d in data:
        if (d["name"] == group):
            return True
    return False


# Get data from request
def get_request_data(request):
    log.info("Get data from request")
    # Get data from request
    if (request.method == "POST"):
        request_data = request.POST.copy()
        request_files = request.FILES
    elif (request.method == "GET"):
        request_data = request.GET.copy()
        request_files = None   
    return request_data, request_files


# Validate user
def validate_user(request, request_data, group):
    log.info("Validating user")
    
    # Verify if user is logged in
    verify_info = verify(request)
    
    # If error wasn't raised update request_data
    if (without_error(verify_info)):
        if (check_if_in_group(verify_info["user"]["groups"], group)):
            # Set user id in request data
            if (request.method == "POST"):
                request_data["user"] = verify_info["user"]["id"]
            elif (request.method == "GET"):
                request_data["user"] = verify_info["user"]["id"]
        else:
            return {"service_message" : "User is not of group " +str(group) +". Forbidden."}
        
        return request_data
    else:
        return verify_info


def safe_send_request(url, data, system, request_type, files = None):
    log.info("Sending "+request_type+" request: "+url )
    try:
        if (request_type == "POST"):
            response = requests.post(url = url, data = data, files = files) 
        elif (request_type == "GET"):
            response = requests.get(url = url, params = data)
        else:
            return {"service_message" : "Unknown type of request"}
    except:
        return {"service_message" : "Service " + str(system) + " is unavailable"}
    
    if (response.status_code != 500):
        return response
    else:
        return {"service_message" : "My mistake. Contact please."}


def send_request(request, system, system_name, auth_need = False, group = False):
    # Get path of url
    path = str(request.path)
    
    # Set url
    url = system + path    

    log.info("Sending request to " + url)
    
    # Get data of request
    data, files = get_request_data(request)
    
    # If auth needed - validating if user logged in
    if (auth_need):
        data = validate_user(request, data, group)
    
    # Send request to server
    if (without_error(data)):
        # Get request
        response = safe_send_request(url, data, system_name, request.method, files)
    else:
        return data
    
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
    log.info("Surfing in filesystem")
    # Get data from FileSystem service
    response = send_request(request, FILE_SYSTEM_URL, "FileSystem", True, "Teacher")
    # If request is OK
    if (without_error(response) and response.status_code == 200):
        # In case of filesystem surfing -> redirect to current folder
        if (dict_name == "fs" and response.content.find("Parent for redirect") != -1):
            s = response.content
            parent = s[s.find("[")+len("]"):s.rfind("]")]
            try:
                return HttpResponseRedirect(GATEWAY_URL + "/file-system/"+str(int(parent))+"/")
            except:
                return HttpResponseRedirect(GATEWAY_URL + "/file-system/")
        else:
            # Get custom json
            data = json.loads(response.content)
        
        # Render page
        response = render(request, template_source, get_dict_by_name(data, dict_name))
        
        # Update auth token
        token_data = refresh(request)
        if (without_error(token_data)):
            response.set_cookie(key='auth_token', value=json.loads(token_data)["token"])
            return response
        else:
            return HttpResponse(token_data["service_message"])
    # Request failed
    else:
        return HttpResponse(response["service_message"])  