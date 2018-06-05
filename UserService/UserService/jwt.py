from django.forms.models import model_to_dict
import json

def jwt_response_payload_handler(token, user=None, request=None):
    user_info = model_to_dict(user)
    user_info["groups"] = list(user.groups.values_list('name',flat=True).values())
    return {
        'token': token,
        'user': user_info,
    }