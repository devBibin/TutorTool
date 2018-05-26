from django.utils import timezone

from models import *


def handle_uploaded_file(f, path):
    cur_time = timezone.now()
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def define_parent(parent_id):
    try:
        parent = Directory.objects.get(pk = parent_id)
        parent_str = str(parent_id)
    except:
        parent = None
        parent_str = ""    
    return parent, parent_str