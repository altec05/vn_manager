from django import forms
from .models import ViPNetNetNumber, Platform, NewAbonent, Owner, ClientName

class ViPNetNetNumberForm(forms.ModelForm):
    class Meta:
        model = ViPNetNetNumber
        fields = ['vipnet_net_number', 'vipnet_net_description']
        widgets = {
            'vipnet_net_number': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'vipnet_net_description': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }

class PlatformForm(forms.ModelForm):
    class Meta:
        model = Platform
        fields = ['platform_name']
        widgets = {
            'platform_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }


class NewAbonentForm(forms.ModelForm):
    class Meta:
        model = NewAbonent
        fields = ['owner', 'client']
        widgets = {
            'owner': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'client': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
        }