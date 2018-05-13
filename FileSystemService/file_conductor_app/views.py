# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User
	
from .forms import UploadFileForm
from django.utils import timezone

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
		print request.POST
		print request.FILES
		if form.is_valid():
			handle_uploaded_file(request.FILES['file'])
			return HttpResponseRedirect(FILE_SYSTEM_URL)
		else:
			print "Invalid form"
	else:
		form = UploadFileForm()
	return render(request, 'file_conductor_app/upload.html', {'form': form})


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
