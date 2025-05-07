from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import NewReq
from .forms import NewReqForm
from Owners.forms import ViPNetNetNumberForm, PlatformForm, NewAbonentForm
from django.http import JsonResponse

class NewReqListView(ListView):
    model = NewReq
    template_name = 'Request/newreq_list.html'
    context_object_name = 'newreqs'


class NewReqDetailView(DetailView):
    model = NewReq
    template_name = 'Request/newreq_detail.html'
    context_object_name = 'newreq'


class NewReqCreateView(CreateView):
    model = NewReq
    form_class = NewReqForm
    template_name = 'Request/newreq_create.html'
    success_url = reverse_lazy('Request:newreq_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['platform_form'] = PlatformForm()
        context['vipnet_net_number_form'] = ViPNetNetNumberForm()
        context['new_abonent_form'] = NewAbonentForm()
        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class NewReqUpdateView(UpdateView):
    model = NewReq
    form_class = NewReqForm
    template_name = 'Request/newreq_update.html'
    success_url = reverse_lazy('Request:newreq_list')


class NewReqDeleteView(DeleteView):
    model = NewReq
    template_name = 'Request/newreq_delete.html'
    success_url = reverse_lazy('Request:newreq_list')

def create_new_abonent(request):
    if request.method == 'POST':
        form = NewAbonentForm(request.POST)
        if form.is_valid():
            owner = form.cleaned_data['owner']
            client = form.cleaned_data['client']
            new_abonent = NewAbonent.objects.create(owner=owner, client=client)
            return JsonResponse({
                'success': True,
                'abonent_id': new_abonent.id,
                'abonent_name': str(new_abonent)
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()})
    return JsonResponse({'success': False, 'errors': 'Invalid request'})


def create_platform(request):
    if request.method == 'POST':
        form = PlatformForm(request.POST)
        if form.is_valid():
            platform = form.save()
            return JsonResponse({
                'success': True,
                'platform_id': platform.id,
                'platform_name': str(platform)
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()})
    return JsonResponse({'success': False, 'errors': 'Invalid request'})


def create_vipnetnetnumber(request):
    if request.method == 'POST':
        form = ViPNetNetNumberForm(request.POST)
        if form.is_valid():
            vipnet_net_number = form.save()
            return JsonResponse({
                'success': True,
                'vipnet_net_number_id': vipnet_net_number.id,
                'vipnet_net_number': str(vipnet_net_number)
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()})
    return JsonResponse({'success': False, 'errors': 'Invalid request'})