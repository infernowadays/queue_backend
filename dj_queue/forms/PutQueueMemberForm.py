from django import forms

class PutQueueMemberForm(forms.Form):
    position = forms.IntegerField(min_value=0)
