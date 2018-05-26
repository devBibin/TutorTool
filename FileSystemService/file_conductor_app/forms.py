from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()

class FolderNameForm(forms.Form):
    name = forms.CharField(max_length=50)