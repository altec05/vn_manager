# Owners/views.py
from django.shortcuts import render
from django.http import JsonResponse
from .forms import ViPNetNetNumberForm, PlatformForm, NewAbonentForm
from .models import ViPNetNetNumber, Platform, NewAbonent

def create_vipnetnetnumber(request):
    if request.method == 'POST':
        form = ViPNetNetNumberForm(request.POST)
        if form.is_valid():
            vipnet_net_number = form.save()
            return JsonResponse({'id': vipnet_net_number.id, 'text': str(vipnet_net_number)})
        else:
            return JsonResponse({'errors': form.errors}, status=400) # Bad Request
    else:
        form = ViPNetNetNumberForm()
    return render(request, 'Owners/vipnetnetnumber_modal_form.html', {'form': form})


def create_platform(request):
    if request.method == 'POST':
        form = PlatformForm(request.POST)
        if form.is_valid():
            platform = form.save()
            return JsonResponse({'id': platform.id, 'text': str(platform)})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = PlatformForm()
    return render(request, 'Owners/platform_modal_form.html', {'form': form})

def create_newabonent(request):
    if request.method == 'POST':
        form = NewAbonentForm(request.POST)
        if form.is_valid():
            owner = form.cleaned_data['owner']
            client = form.cleaned_data['client']
            new_abonent = NewAbonent.objects.create(owner=owner, client=client)

            return JsonResponse({'id': new_abonent.id, 'text': str(new_abonent)})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = NewAbonentForm()
    return render(request, 'Owners/newabonent_modal_form.html', {'form': form})
