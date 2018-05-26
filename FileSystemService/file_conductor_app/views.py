# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
    
from .forms import UploadFileForm, FolderNameForm
from models import *
from utils import *

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILE_SYSTEM_URL = "http://localhost:8000/"

def index(request):
    print user_auth(request)
    return render(request, 'file_conductor_app/base.html')


def create_repo(request):
    # Get current user
    user = request.user
    
    # Create filesystem
    fs = FileSystem.objects.create(master = user)
    
    # Create service's directories
    Directory.objects.create(file_system=fs, name="Temp", is_editable=False)

    return HttpResponse("Created for " + str(user.username))


def get_dir(request, folder_id=None, message=None):
    # Get current user
    user = request.user

    # Get all info about current directory in current filesystem
    fs = FileSystem.objects.get(master= user)
    dirs = Directory.objects.filter(file_system=fs, parent=folder_id)
    files = File.objects.filter(file_system=fs, parent=folder_id)
    tests = Test.objects.filter(file_system=fs, parent=folder_id)
    questions = Question.objects.filter(file_system=fs, parent=folder_id)
    
    # Get forms
    upload_form = UploadFileForm()
    dir_form = FolderNameForm()
    
    # Return result
    return render(request, "file_conductor_app/file_system.html", 
        {"dirs" : dirs,
         "files" : files,
         "tests" : tests,
         "questions": questions,
         "upload_form" : upload_form,
         "dir_form" : dir_form,
         "message" : message,
         })


def create_folder(request, parent_id=None):
    # Get parent folder
    parent, parent_str = define_parent(parent_id)
    if (request.method == "POST"):
        # Get user
        user = request.user
        # Get filesystem of user
        fs = FileSystem.objects.get(master= user)
        # Get form
        form = FolderNameForm(request.POST)
        if form.is_valid():
            Directory.objects.create(file_system=fs, parent=parent, name = form.cleaned_data["name"])
            return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/" + parent_str)
        else:
            return HttpResponse("Form is invalid", 400)


def upload_file(request, parent_id=None):
    # Get parent directory
    parent, parent_str = define_parent(parent_id)

    if request.method == 'POST':
        # Get user
        user = request.user
        
        # Get filesystem
        fs = FileSystem.objects.get(master=user)
        
        # Get upload file form
        form = UploadFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Set path for teachers repository
            path = os.path.join(BASE_DIR + "/../teachers_repositories/", str(user.pk) +"_"+str(user.username))
            try:
                # Create folder if not exist
                os.mkdir(path)
            except:
                pass
            
            # Uploading to harddrive
            handle_uploaded_file(request.FILES['file'], path + str("/") + str(user.username) +"_"+ timezone.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # Create file object
            File.objects.create(file_system = fs,
                name=form.cleaned_data["name"], 
                parent=parent, 
                path=path, 
                internal_name = str(user.username) +"_"+ timezone.now().strftime("%Y-%m-%d %H:%M:%S"))
            return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/" + parent_str)
        else:
            return HttpResponse("Form is invalid", 400)


def user_auth(request):
    username = "xxx"
    password = "000"
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return True
    else:
        return False