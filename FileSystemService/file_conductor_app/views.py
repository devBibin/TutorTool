# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.core import serializers
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt

from models import *
from utils import *

import json
import os
import re

FILE_SYSTEM_URL = "http://localhost:8001/"

#==============================================================================
#=======================CREATE REPOSITORY======================================
@csrf_exempt
def create_repo(request):
    # Get current user
    user = get_user_id(request)
    
    # Create filesystem
    fs = FileSystem.objects.create(master = user)
    
    # Create service's directories
    Directory.objects.create(file_system=fs, 
        name="Temp", 
        is_editable=False, 
        can_be_deleted=False)

    return HttpResponse("Repository was created. Parent for redirect [" + str(None) + "]")
#==============================================================================


#==============================================================================
#===============================FOLDER API=====================================
@csrf_exempt
def get_folder(request, folder_id=None):
    # Get current user
    print request.user
    user = get_user_id(request)     
    if (request.method == "GET"):
        # Get all info about current directory in current filesystem
        fs = FileSystem.objects.get(master= user)
        dirs = Directory.objects.filter(file_system=fs, parent=folder_id, is_deleted=False)
        files = File.objects.filter(file_system=fs, parent=folder_id, is_deleted=False)
        tests = Test.objects.filter(file_system=fs, parent=folder_id, is_deleted=False)
        questions = Question.objects.filter(file_system=fs, parent=folder_id, is_deleted=False)
        

        # Get status of FileSystem
        test_id = ""
        if (fs.status == "surfing"):
            title = "Ваша файловая система"
            mode = 0
        elif (fs.status == "transfering"):
            title = "Выберите директорию, где будет храниться объект"
            mode = 1
        elif (fs.status == "collecting_test"):
            # Set current test id and get object
            test_id = fs.temp_id
            t = Test.objects.get(pk = test_id)

            title = "Выберите вопросы для включения в тест: " + t.name
            mode = 2
        else:
            print "Краш: неизвестный статус файловой системы"

        # Get parent directory
        try:
            master = Directory.objects.get(pk=folder_id)
            master = model_to_dict(master)
        except:
            master = None
        
        # Return result
        return JsonResponse(
            {"dirs" : list(dirs.values()),
             "files" : list(files.values()),
             "tests" : list(tests.values()),
             "questions": list(questions.values()),
             "master": master,
             "mode": mode,
             "title": title,
             "test_id": test_id,
             })


@csrf_exempt
def create_folder(request, parent_id=None):
    # Get current user
    user = get_user_id(request) 
    if (request.method == "POST"):
        # Get parent folder
        parent, parent_str = define_parent(parent_id)
        # Get filesystem of user
        fs = FileSystem.objects.get(master=int(user))
        # Get folder name
        name = request.POST.get("name")
        # Create folder
        Directory.objects.create(file_system=fs, parent=parent, name = name)
        
        return HttpResponse("Folder was created. Parent for redirect [" + str(parent_id) + "]")


@csrf_exempt
def remove_folder(request, id):
    # Get current user
    user = get_user_id(request) 
    if (request.method == "GET"):

        # Get and set deleted flag
        d = Directory.objects.get(pk=id)
        d.is_deleted = True
        d.save()

        # Get current folder
        parent, parent_str = define_parent(d.parent_id)

        # Return result
        return HttpResponse("Folder was removed. Parent for redirect [" + str(parent_str) + "]")
#==============================================================================
#==============================================================================



#==============================================================================
#=================================FILE API=====================================
@csrf_exempt
def upload_file(request, parent_id=None):
    # Get current user
    user = get_user_id(request)     
    if (request.method == 'POST'):
        # Get parent directory
        parent, parent_str = define_parent(parent_id)

        # Get filename
        filename = request.FILES['file'].name
        
        # Get filesystem
        fs = FileSystem.objects.get(master=user)
        
        # Set path for teachers repository
        path = os.path.join(settings.BASE_DIR + "/../teachers_repositories/", str(user))
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
        return HttpResponse("File was uploaded. Parent for redirect [" + str(parent_str) + "]")


@csrf_exempt
def download_file(request, id):
    # SECURITY WARNING
    # Get current user
    user = get_user_id(request) 

    if (request.method == "GET"):
        f_obj = File.objects.get(pk=id)
        file_path = f_obj.path + "/" + f_obj.name
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
        raise Http404


@csrf_exempt
def remove_file(request, id):
    # Get current user
    user = get_user_id(request) 
    if (request.method == "GET"):

        # Get and set deleted flag
        f = File.objects.get(pk=id)
        f.is_deleted = True
        f.save()

        parent, parent_str = define_parent(f.parent_id)
        
        # Return result
        return HttpResponse("File was removed. Parent for redirect [" + str(parent_str) + "]")
#==============================================================================
#==============================================================================



#==============================================================================
#==============================QUESTIONS API===================================
@csrf_exempt
def add_question(request):
    # Get current user
    user = get_user_id(request)     
    if (request.method == "POST"):
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


@csrf_exempt
def remove_question(request, id):
    # Get current user
    user = get_user_id(request) 
    if (request.method == "GET"):

        # Get and set deleted flag
        q = Question.objects.get(pk=id)
        q.is_deleted = True
        q.save()

        parent, parent_str = define_parent(q.parent_id)
        
        # Return result
        return HttpResponse("File was removed. Parent for redirect [" + str(parent_str) + "]")


@csrf_exempt
def get_question(request, question_id):
    # Get current user
    user = get_user_id(request) 
    q = Question.objects.get(pk=question_id)
    qc = QuestionChoices.objects.filter(question = q)
    return JsonResponse(
        {"question" : model_to_dict(q),
         "questionchoices" : list(qc.values()),}
        )
#==============================================================================


#==============================================================================
#==============================TEST API========================================
@csrf_exempt
def add_test(request):
    # Get current user
    user = get_user_id(request)    
    if (request.method == "POST"):
        # Get POST data
        name = request.POST.get("name")
        description = request.POST.get("description")
        time = request.POST.get("time")
        
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

        fs = FileSystem.objects.get(master = user)
        fs.status = "collecting_test"
        fs.temp_id = t.pk
        fs.save()
        
        return HttpResponse("Test was created. Parent for redirect [" + str(None) + "]")


@csrf_exempt
def get_test(request, test_id):
    # Get current user
    user = get_user_id(request) 
    t = Test.objects.get(pk=test_id)
    qref = list(QuestionToTest.objects.filter(test = t).values())
    print qref
    for i in range(len(qref)):
        q = Question.objects.get(pk = qref[i]["question_id"])
        qref[i]["question_id"] = model_to_dict(q)
    print qref
    return JsonResponse({
        "test" : model_to_dict(t),
        "questions": qref,
        })


@csrf_exempt
def remove_test(request, id):
    # Get current user
    user = get_user_id(request) 
    if (request.method == "GET"):

        # Get and set deleted flag
        t = Test.objects.get(pk=id)
        t.is_deleted = True
        t.save()

        parent, parent_str = define_parent(t.parent_id)
        
        # Return result
        return HttpResponse("File was removed. Parent for redirect [" + str(parent_str) + "]")


@csrf_exempt
def search_for_test(request, test_id):
    # Get current user
    user = get_user_id(request) 
    t = Test.objects.get(pk=test_id)
    
    # Get FileSystem and set status collecting test
    fs = FileSystem.objects.get(master = user)
    fs.status = "collecting_test"
    fs.temp_id = test_id
    fs.save()

    return HttpResponse("Test was created. Parent for redirect [" + str(None) + "]")


@csrf_exempt
def submit_test(request, test_id):
    # Get current user
    user = get_user_id(request) 
    
    # Get FileSystem and set status transfering test
    fs = FileSystem.objects.get(master = user)
    fs.status = "transfering"
    fs.temp_transfer_type = "test"
    fs.save()    
    
    return HttpResponse("Test was submitted. Parent for redirect [" + str(None) + "]")


@csrf_exempt
def add_question_to_test(request, question_id, test_id):
    # Get current user
    user = get_user_id(request) 
    
    # Get question and test
    q = Question.objects.get(pk = question_id)
    t = Test.objects.get(pk = test_id)
    
    # Get current index of question
    index = len(QuestionToTest.objects.filter(test = t))
    
    # Create object
    QuestionToTest.objects.create(question = q, test = t, q_index_in_test = index + 1)
    
    # Redirect to currenr folder
    parent, parent_str = define_parent(q.parent_id)
    return HttpResponse("Question added to test. Parent for redirect [" + str(parent_str) + "]")  
#==============================================================================



#==============================================================================
#===========================TRANSFERING OBJECTS API============================
@csrf_exempt
def transfer_object(request, object_type, object_id):
    user = get_user_id(request)
    
    # Get FileSystem and set status transferring for object_id of type object_type
    fs = FileSystem.objects.get(master = user)
    fs.status = "transfering"
    fs.temp_transfer_type = object_type
    fs.temp_id = object_id
    fs.save()
    
    return HttpResponse("Object of type: " +str(object_type)+" and id: "+str(object_id)+" is transferring. Parent for redirect [" + str(None) + "]")


@csrf_exempt
def submit_transfer(request, parent_id = None):
    # WARNING SECURITY!!!
    user = get_user_id(request)
    fs = FileSystem.objects.get(master = user)
    
    # Get type and id of the object
    object_type = fs.temp_transfer_type
    pk = fs.temp_id
    
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

    # If object is dir and user tries to push dir to itself
    if (pk == parent_id) and (object_type == "dir"):
        fs.temp_transfer_type = None
        fs.temp_id = None
        fs.status = "surfing"
        fs.save()
        return HttpResponse("Object wasn't transfered: recursive error. Parent for redirect [" + str(None) + "]", status = 400)

    # Change parent of the object
    cur_obj.last_upd = timezone.now()
    cur_obj.upd_type = "Transfer"
    cur_obj.parent_id = parent_id
    cur_obj.save()

    # Change status of FileSystem to surfing
    fs.temp_transfer_type = None
    fs.temp_id = None
    fs.status = "surfing"
    fs.save()

    # Redirect to current folder
    if (parent_id == None):
        return HttpResponse("Object was transfered. Parent for redirect [" + str(None) + "]")
    else:
       return HttpResponse("Object was transfered. Parent for redirect [" + str(parent_id) + "]")
#==============================================================================