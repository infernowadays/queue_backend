from django import forms


class NewQueueMemberForm(forms.Form):
    name = forms.CharField(max_length=50)
    position = forms.IntegerField(min_value=0)
