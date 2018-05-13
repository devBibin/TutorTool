# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
from .forms import UploadFileForm, FolderNameForm
from django.utils import timezone

from models import *

FILE_SYSTEM_URL = "http://localhost:8000/"

def handle_uploaded_file(f, path):
    cur_time = timezone.now()
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def index(request):
    print user_auth(request)
    return render(request, 'file_conductor_app/base.html')

def create_repo(request):
    username = None
    if request.user.is_authenticated():
        user = request.user
    fs = FileSystem.objects.create(master = user)
    Directory.objects.create(file_system=fs, name="Temp", is_editable=False)
    return HttpResponse("Created for " + str(user.username))


def get_dir(request, folder_id=None, message=None):
    user = request.user

    fs = FileSystem.objects.get(master= user)
    dirs = Directory.objects.filter(file_system=fs, parent=folder_id)
    files = File.objects.filter(file_system=fs, parent=folder_id)
    tests = Test.objects.filter(file_system=fs, parent=folder_id)
    questions = Question.objects.filter(file_system=fs, parent=folder_id)
    
    upload_form = UploadFileForm()
    dir_form = FolderNameForm()
    return render(request, "file_conductor_app/file_system.html", 
        {"dirs" : dirs,
         "files" : files,
         "tests" : tests,
         "questions": questions,
         "upload_form" : upload_form,
         "dir_form" : dir_form,
         "message" : message})


def define_parent(parent_id):
    try:
        parent = Directory.objects.get(pk = parent_id)
        parent_str = str(parent_id)
    except:
        parent = None
        parent_str = ""    
    return parent, parent_str


def create_folder(request, parent_id=None):
    parent, parent_str = define_parent(parent_id)
    if (request.method == "POST"):
        user = request.user
        fs = FileSystem.objects.get(master= user)
        form = FolderNameForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            Directory.objects.create(file_system=fs, parent=parent, name = form.cleaned_data["name"])
            return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/" + parent_str)
        else:
            return HttpResponse("Form is invalid", 400)
    else:
        return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/" + str(parent_id))


def upload_file(request, parent_id=None):
    parent, parent_str = define_parent(parent_id)

    if request.method == 'POST':
        user = request.user
        fs = FileSystem.objects.get(master=user)
        form = UploadFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            path = os.path.join(BASE_DIR + "/../teachers_repositories/", str(user.pk) +"_"+str(user.username))
            try:
                os.mkdir(path)
            except:
                pass    
            handle_uploaded_file(request.FILES['file'], path + str("/") + str(user.username) +"_"+ timezone.now().strftime("%Y-%m-%d %H:%M:%S"))
            File.objects.create(file_system = fs,
                name=form.cleaned_data["name"], 
                parent=parent, 
                path=path, 
                internal_name = str(user.username) +"_"+ timezone.now().strftime("%Y-%m-%d %H:%M:%S"))
            return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/" + parent_str)
        else:
            return HttpResponse("Form is invalid", 400)
    else:
        return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/" + str(parent_id))








def auth(request):
    username = "xxx"
    password = "000"
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return True
    else:
        return False