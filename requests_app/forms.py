from django import forms

from .models import Request


class RequestCreateForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ["client_name", "phone", "address", "problem_text"]
        widgets = {"problem_text": forms.Textarea(attrs={"rows": 4})}
