# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User
	
from .forms import UploadFileForm, FolderNameForm
from django.utils import timezone

from models import *

FILE_SYSTEM_URL = "http://localhost:8000/"

def handle_uploaded_file(f):
	cur_time = timezone.now()
	with open(str(cur_time), 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

def index(request):
	print user_auth(request)
	return render(request, 'file_conductor_app/base.html')


def upload(request):
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			handle_uploaded_file(request.FILES['file'])
			return HttpResponseRedirect(FILE_SYSTEM_URL)
		else:
			print "Invalid form"
	else:
		form = UploadFileForm()
	return render(request, 'file_conductor_app/upload.html', {'form': form})

def create_repo(request):
	username = None
	if request.user.is_authenticated():
		user = request.user
	fs = FileSystem.objects.create(master = user)
	Directory.objects.create(file_system=fs, name="Temp", is_editable=False)
	return HttpResponse("Created for " + str(user.username))


def get_dir(request, folder_id=None, message=None):
	if (request.method == "GET"):
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
	else:
		return HttpResponse("Bad request", 400)


def create_folder(request, parent_id=None):
	if (request.method == "POST"):
		user = request.user
		fs = FileSystem.objects.get(master= user)
		form = FolderNameForm(request.POST) # A form bound to the POST data
		if form.is_valid():
			Directory.objects.create(file_system=fs, parent=parent_id, name = form["name"])
			return get_dir(request, parent_id, "Folder successfully created.")
		else:
			return get_dir(request, parent_id, "Folder wasn't created. Bad data in form.")


		









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