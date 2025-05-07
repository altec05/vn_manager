# from django import forms
# from .models import NewReq
#
# class NewReqForm(forms.ModelForm):
#     class Meta:
#         model = NewReq
#         fields = ['date', 'number_naumen', 'number_elk', 'ogv', 'amount', 'abonents', 'platform', 'net_number', 'note']
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date'}),
#             'date_of_release': forms.DateInput(attrs={'type': 'date'}),
#             'note': forms.Textarea(attrs={'rows': 3}),
#         }
#

# Request/forms.py
from django import forms
from .models import NewReq
from Owners.models import Owner, ClientName, NewAbonent, Platform, ViPNetNetNumber

class NewReqForm(forms.ModelForm):
    class Meta:
        model = NewReq
        fields = ['date', 'number_naumen', 'number_elk', 'ogv', 'amount', 'abonents', 'platform', 'net_number', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'number_naumen': forms.TextInput(attrs={'class': 'form-control'}),
            'number_elk': forms.TextInput(attrs={'class': 'form-control'}),
            'ogv': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'abonents': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'platform': forms.Select(attrs={'class': 'form-select'}),
            'net_number': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ['full_name']

class ClientNameForm(forms.ModelForm):
    class Meta:
        model = ClientName
        fields = ['client_name']

class NewAbonentForm(forms.ModelForm):
    class Meta:
        model = NewAbonent
        fields = ['owner', 'client']

class PlatformForm(forms.ModelForm):
    class Meta:
        model = Platform
        fields = ['platform_name']

class ViPNetNetNumberForm(forms.ModelForm):
    class Meta:
        model = ViPNetNetNumber
        fields = ['vipnet_net_number', 'vipnet_net_description']