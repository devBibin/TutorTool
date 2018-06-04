from django.forms.models import model_to_dict

def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': model_to_dict(user)
    }