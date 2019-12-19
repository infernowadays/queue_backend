import json
from django import forms
from rest_framework.exceptions import ValidationError


class InvitationForm(forms.Form):
    login = forms.CharField(required=False)
    shortSqToken = forms.CharField(required=False)


class InvitationsField(forms.Field):
    def to_python(self, value):
        # Empty list if no invitations are provided
        if not value:
            return []

        invitation_forms = [InvitationForm(data) for data in value]
        return invitation_forms


class QueueForm(forms.Form):
    name = forms.CharField(max_length=50)
    description = forms.CharField(required=False, max_length=500)
    invitations = InvitationsField(required=False)

    def clean_invitations(self):
        invitation_forms = self.cleaned_data['invitations']
        invitations = []
        for i, invitation_form in enumerate(invitation_forms):
            if not invitation_form.is_valid():
                for prop, propErrors in invitation_form.errors.items():
                    for err in propErrors.data:
                        err.path = f'invitations[{i}].{prop}'
                        self.add_error('invitations', err)
            else:
                login = invitation_form.cleaned_data['login']
                if len(login) < 1:
                    login = None
                invitations.append({
                    'login': login,
                    'shortSqToken': invitation_form.cleaned_data['shortSqToken']
                })
        return invitations
