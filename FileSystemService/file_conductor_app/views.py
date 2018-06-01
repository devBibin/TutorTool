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

import os

FILE_SYSTEM_URL = "http://localhost:8000/"

def index(request):
    print user_auth(request)
    return render(request, 'file_conductor_app/base.html')


def create_repo(request):
    if (request.method == "POST"):
        # Get current user
        user = request.user
        
        # Create filesystem
        fs = FileSystem.objects.create(master = user)
        
        # Create service's directories
        Directory.objects.create(file_system=fs, 
            name="Temp", 
            is_editable=False, 
            can_be_deleted=False)

        return HttpResponse("Created for " + str(user.username))


def get_folder(request, folder_id=None):
    if (request.method == "GET"):
        # Get current user
        user = request.user

        # Get all info about current directory in current filesystem
        fs = FileSystem.objects.get(master= user)
        dirs = Directory.objects.filter(file_system=fs, parent=folder_id, is_deleted=False)
        files = File.objects.filter(file_system=fs, parent=folder_id, is_deleted=False)
        tests = Test.objects.filter(file_system=fs, parent=folder_id, is_deleted=False)
        questions = Question.objects.filter(file_system=fs, parent=folder_id, is_deleted=False)
        
        # Get parent directory
        try:
            master = Directory.objects.get(pk=folder_id)
        except:
            master = None
        
        # Return result
        return render(request, "file_conductor_app/file_system.html", 
            {"dirs" : dirs,
             "files" : files,
             "tests" : tests,
             "questions": questions,
             "master": master,
             })


def create_folder(request, parent_id=None):
    if (request.method == "POST"):
        # Get parent folder
        parent, parent_str = define_parent(parent_id)
        # Get user
        user = request.user
        # Get filesystem of user
        fs = FileSystem.objects.get(master=user)
        # Get folder name
        name = request.POST.get("name")
        # Create folder
        Directory.objects.create(file_system=fs, parent=parent, name = name)
        
        return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/" + parent_str)


def remove_folder(request, id):
    if (request.method == "GET"):
        # Get current user
        user = request.user

        # Get and set deleted flag
        d = Directory.objects.get(pk=id)
        d.is_deleted = True
        d.save()

        # Get current folder
        parent, parent_str = define_parent(d.parent_id)
        
        # Return result
        return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/" + parent_str)


def upload_file(request, parent_id=None):
    if (request.method == 'POST'):
        # Get parent directory
        parent, parent_str = define_parent(parent_id)
        
        # Get user
        user = request.user

        # Get filename
        filename = request.FILES['file'].name
        
        # Get filesystem
        fs = FileSystem.objects.get(master=user)
        
        # Set path for teachers repository
        path = os.path.join(settings.BASE_DIR + "/../teachers_repositories/", str(str(user.pk)+"_"+str(user.username)))
        try:
            # Create folder if not exist
            os.mkdir(path)
        except:
            pass

        # Uploading to harddrive
        handle_uploaded_file(request.FILES['file'], path + str("/") + filename)
        
        # Create file object
        File.objects.create(file_system = fs,
            name=filename, 
            parent=parent, 
            path=path, 
            )
        return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/" + parent_str)


def download_file(request, id):
    if (request.method == "GET"):
        f_obj = File.objects.get(pk=id)
        file_path = f_obj.path + "/" + f_obj.name
        print file_path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
        raise Http404


def remove_file(request, id):
    if (request.method == "GET"):    
        # Get current user
        user = request.user

        # Get and set deleted flag
        f = File.objects.get(pk=id)
        f.is_deleted = True
        f.save()

        parent, parent_str = define_parent(f.parent_id)
        
        # Return result
        return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/" + parent_str)


def add_question(request):
    if (request.method == "GET"):
        return render(request, 'file_conductor_app/question.html')
    elif (request.method == "POST"):
        # Get POST data
        name = request.POST.get("name")
        body = request.POST.get("body")
        answer_type = request.POST.get("answer_type")
        rate = request.POST.get("rate")
        choices = []
        for i in range(1,11):
            item = {}
            # Get text
            item["choice"] = request.POST.get("choice"+str(i))
            
            # Get is_true flag
            if (request.POST.get("is_true"+str(i)) == "on"):
                item["is_true"] = True
            else:
                item["is_true"] = False

            # Append if text is not empty
            if (len(item["choice"]) > 0):
                choices.append(item)
        
        # Get current user
        user = request.user
        
        # Get filesystem
        fs = FileSystem.objects.get(master=user)
        
        # Get Temp directory
        directory = Directory.objects.get(file_system=fs, name = "Temp")      

        # Save question
        q = Question.objects.create(file_system = fs,
            name=name,
            bodytext=body,
            parent=directory,
            answer_type=answer_type,
            rate=rate,
            )
        # Save question choices
        for item in choices:
            QuestionChoices.objects.create(question= q,
                text = item["choice"],
                is_true= item["is_true"])

        return HttpResponse("OK")


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