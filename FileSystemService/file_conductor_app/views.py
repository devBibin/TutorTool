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

#==============================================================================
#==========================TEMP FUNCTIONS======================================
def index(request):
    print user_auth(request)
    return render(request, 'file_conductor_app/base.html')


def user_auth(request):
    username = "foo"
    password = "bar"
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return True
    else:
        return False
#==============================================================================


#==============================================================================
#=======================CREATE REPOSITORY======================================
def create_repo(request):
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
#==============================================================================


#==============================================================================
#===============================FOLDER API=====================================
def get_folder(request, folder_id=None):
    if (request.method == "GET"):
        test_id = ""
        mode = 0
        title = "Ваша файловая система"
        if 'test_id' in request.session:
            t = Test.objects.get(pk = str(request.session["test_id"]))
            title = "Выберите вопросы для включения в тест: " + t.name
            mode = 2
            test_id = request.session["test_id"]
        elif 'object_type' in request.session and 'object_id' in request.session:
            title = "Выберите директорию, где будет храниться объект"
            mode = 1
        
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
             "mode": mode,
             "title": title,
             "test_id": test_id,
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
#==============================================================================
#==============================================================================



#==============================================================================
#=================================FILE API=====================================
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
#==============================================================================
#==============================================================================



#==============================================================================
#==============================QUESTIONS API===================================
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
            body=body,
            parent=directory,
            answer_type=answer_type,
            rate=rate,
            )
        # Save question choices
        for item in choices:
            QuestionChoices.objects.create(question= q,
                text = item["choice"],
                is_true= item["is_true"])

        return transfer_object(request, "question", q.pk)


def get_question(request, question_id):
    q = Question.objects.get(pk=question_id)
    qc = QuestionChoices.objects.filter(question = q)
    return render(request, 'file_conductor_app/question.html',
        {
        "question": q,
        "questionchoices" : qc,
        })
#==============================================================================


#==============================================================================
#==============================TEST API========================================
def add_test(request):
    if (request.method == "GET"):
        return render(request, 'file_conductor_app/test.html')
    elif (request.method == "POST"):
        # Get POST data
        name = request.POST.get("name")
        description = request.POST.get("description")
        time = request.POST.get("time")

        # Get current user
        user = request.user
        
        # Get filesystem
        fs = FileSystem.objects.get(master=user)
        
        # Get Temp directory
        directory = Directory.objects.get(file_system=fs, name = "Temp")      

        # Save question
        t = Test.objects.create(file_system = fs,
            name=name,
            description=description,
            time=time,
            parent=directory,
            )

        request.session["test_id"] = t.pk
        request.session['object_id'] = t.pk
        request.session['object_type'] = "test"
        return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/")


def get_test(request, test_id):
    t = Test.objects.get(pk=test_id)
    qref = QuestionToTest.objects.filter(test = t)
    return render(request, 'file_conductor_app/test.html',
        {"test" : t,
        "questions": qref})


def search_for_test(request, test_id):
    t = Test.objects.get(pk=test_id)
    request.session["test_id"] = t.pk
    return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/")


def submit_test(request):
    del request.session['test_id']
    return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/")

def add_question_to_test(request, question_id, test_id):
    q = Question.objects.get(pk = question_id)
    t = Test.objects.get(pk = test_id)
    index = len(QuestionToTest.objects.filter(test = t))
    QuestionToTest.objects.create(question = q, test = t, q_index_in_test = index + 1)
    parent, parent_str = define_parent(q.parent_id)
    return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/" + parent_str)   
#==============================================================================



#==============================================================================
#===========================TRANSFERING OBJECTS API============================
def transfer_object(request, object_type, object_id):
    request.session['object_id'] = object_id
    request.session['object_type'] = object_type
    return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/")


def submit_transfer(request, parent_id = None):
    # WARNING SECURITY!!!
    pk = request.session['object_id']
    object_type = request.session['object_type']
    # Get object
    if (object_type == "dir"):
        cur_obj = Directory.objects.get(pk = pk)
    elif (object_type == "file"):
        cur_obj = File.objects.get(pk = pk)
    elif (object_type == "question"):
        cur_obj = Question.objects.get(pk = pk)
    elif (object_type == "test"):
        cur_obj = Test.objects.get(pk = pk)
    else:
        pass

    if (pk == parent_id) and (object_type == "dir"):
        del request.session['object_type']
        del request.session['object_id']
        request.session.modified = True
        return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/")

    cur_obj.last_upd = timezone.now()
    cur_obj.upd_type = "Transfer"
    cur_obj.parent_id = parent_id
    cur_obj.save()

    del request.session['object_type']
    del request.session['object_id']
    request.session.modified = True
    if (parent_id):
        return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/" + str(parent_id))
    else:
        return HttpResponseRedirect(FILE_SYSTEM_URL + "file-system/")
#==============================================================================