# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict

from models import *

@csrf_exempt
def register(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    group = request.POST.get("group")

    try:
        User.objects.get(username= username)
        return HttpResponse("User " + str(username) + " is already exists", status = 400)
    except:
        g = Group.objects.get(name = group)
        u = User.objects.create_user(username,
            password = password)
        u.groups.add(g)
        if (group == "Teacher"):
            TeacherInfo.objects.create(user = u)
        else:
            StudentInfo.objects.create(user = u)

        return HttpResponse(u.pk)

@csrf_exempt
def get_info(request, user_id):
    u = User.objects.get(pk = user_id)
    if (u.groups.filter(name='Teacher').exists()):
        g = "Teacher"
    elif (u.groups.filter(name='Student').exists()):
        g = "Student"
    else:
        return HttpResponse("Unknown type of user", status = 400)

    if (g == "Teacher"):
        info = TeacherInfo.objects.get(user = u)
        relations = StudentToTeacher.objects.filter(teacher = u, status = "Active")
    else:
        info = StudentInfo.objects.get(user = u)
        relations = StudentToTeacher.objects.filter(student = u, status = "Active")
    
    response = {}
    
    user_info = model_to_dict(u)
    user_info["groups"] = list(u.groups.values_list('name',flat=True).values())
    response["user_info"] = user_info
    
    response["special_info"] = model_to_dict(info)
    
    response["relations"] = []
    for r in relations:
        if (g == "Teacher"):
            student_info = model_to_dict(r.student)
            student_info["groups"] = list(r.student.groups.values_list('name',flat=True).values())
            response["relations"].append(student_info)
        else:
            teacher_info = model_to_dict(r.teacher)
            teacher_info["groups"] = list(r.teacher.groups.values_list('name',flat=True).values())
            response["relations"].append(teacher_info)
    return JsonResponse(response)


@csrf_exempt
def subscribe(request, student_id, teacher_id):
    s = User.objects.get(pk = student_id)
    t = User.objects.get(pk = teacher_id)
    if (s.groups.filter(name='Student').exists() and t.groups.filter(name='Teacher').exists()):
        try:
            StudentToTeacher.objects.get(student = s, teacher = t)
            return HttpResponse("Student tried to subscribe teacher")
        except:
            StudentToTeacher.objects.create(student = s, teacher = t)
            return HttpResponse("Student " + s.username + " subscribed to " + t.username)
    else:
        return HttpResponse("Only student can subscribe to teacher")


@csrf_exempt
def confirm(request, student_id, teacher_id):
    s = User.objects.get(pk = student_id)
    t = User.objects.get(pk = teacher_id)
    try:
        st = StudentToTeacher.objects.get(student = s, teacher = t)
        st.status = "Active"
        st.save()
        return HttpResponse("Teacher " + t.username + " confirmed " + s.username)
    except:
        return HttpResponse("Relation not found")


@csrf_exempt
def decline(request, student_id, teacher_id):
    s = User.objects.get(pk = student_id)
    t = User.objects.get(pk = teacher_id)
    try:
        st = StudentToTeacher.objects.get(student = s, teacher = t)
        if (st.status == "Active"):
            status = "Canceled"
            st.status = status
            st.save()
        elif (st.status == "Pending"):
            status = "Refused"
            st.status = status
            st.save()

        return HttpResponse("Teacher " + t.username + " "+status+" " + s.username)
    except:
        return HttpResponse("Relation not found")


@csrf_exempt
def has_relations(request, student_id, teacher_id):
    s = User.objects.get(pk = student_id)
    t = User.objects.get(pk = teacher_id)
    if (s.groups.filter(name='Student').exists() and t.groups.filter(name='Teacher').exists()):
        try:
            StudentToTeacher.objects.get(student = s, teacher = t, status = "Active")
            return HttpResponse("OK")
        except:
            return HttpResponse("Not OK", status=400)
    else:
        return HttpResponse("Groups error", status = 400)