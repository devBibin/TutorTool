from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict

from models import *
import json

@csrf_exempt
def add_lesson(request, teacher_id, student_id):
	Lesson.objects.create(teacher = teacher_id, 
		student = student_id, 
		info = request.POST.get("info"))
	return HttpResponse("Lesson was added")


@csrf_exempt
def add_homework_item(request, lesson_id, object_type, object_id):
	teacher =request.POST.get("user")
	try:
		l = Lesson.objects.get(teacher = teacher, pk = lesson_id)
	except:
		return HttpResponse("Lesson doesn't exist", status = 400)
	Homework.objects.create(lesson = l, object_type = object_type, object_id = object_id)
	return HttpResponse("Home work item was added")


@csrf_exempt
def get_lessons(request, teacher_id, student_id):
	teacher_id = int(teacher_id)
	student_id = int(student_id)
	if (student_id != 0 and teacher_id != 0):
		ls = Lesson.objects.filter(student = student_id, teacher = teacher_id)
	elif (student_id == 0):
		ls = Lesson.objects.filter(teacher = teacher_id)
	elif (teacher_id == 0):
		ls = Lesson.objects.filter(student = student_id)
	else:
		return HttpResponse("Unknown teacher and student")
	
	response = []
	for l in ls:
		item = {}
		item["lesson"] = model_to_dict(l)
		h = Homework.objects.filter(lesson = l)
		item["homework"] = list(h.values())
		print item
		response.append(item)
	return JsonResponse(response, safe=False)


@csrf_exempt
def has_student_access(request, student_id, object_type, object_id):
	if (Homework.objects.filter(student = student_id, object_type = object_type, object_id = object_id).len() > 0):
		return HttpResponse("OK")
	else:
		return HttpResponse("Not OK", status = 400)