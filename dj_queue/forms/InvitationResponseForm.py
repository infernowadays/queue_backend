from django import forms

from dj_queue.enums import Decision


class InvitationResponseForm(forms.Form):
    decision = forms.ChoiceField(choices=Decision.choices())
