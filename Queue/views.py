from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Prefetch
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.http import HttpResponseRedirect

from Owners.models import NewAbonent
from .models import NewRecipient
from .forms import NewRecipientForm, RecipientFilterForm


class NewRecipientListView(ListView):
    model = NewRecipient
    template_name = 'Queue/newrecipient_list.html'
    context_object_name = 'recipients'
    paginate_by = 10  # Добавьте пагинацию, если нужно

    def get_queryset(self):
        queryset = super().get_queryset()
        #  Не передаем self.request.GET при первом открытии
        if self.request.GET:
            self.form = RecipientFilterForm(self.request.GET)
            if self.form.is_valid():
                status = self.form.cleaned_data.get('status')
                if status:
                    queryset = queryset.filter(status=status)
        else:
             self.form = RecipientFilterForm() # Создаем форму без данных
             queryset = queryset.filter(status='pending')


        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.form  # Передайте форму в шаблон
        # Добавляем словарь с классами статусов в контекст
        context['status_classes'] = {
            'released': 'status-released',
            'pending': 'status-pending',
            'completed': 'status-completed',
        }
        return context

class NewRecipientDetailView(DetailView):
    model = NewRecipient
    template_name = 'Queue/newrecipient_detail.html'
    context_object_name = 'recipient'

    def get_queryset(self):
        # Оптимизируем запрос
        return super().get_queryset().select_related('request').prefetch_related(
            Prefetch(
                'request__abonents',
                queryset=NewAbonent.objects.select_related('client')  # Оптимизируем связь NewAbonent с Client
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipient = self.get_object()
        clients = []

        try:
            if recipient.request:
                for abonent in recipient.request.abonents.all():
                    clients.append(abonent.client.client_name)
        except AttributeError:
            # Обрабатываем случай, когда request is None
            clients = []  # Или какое-то другое значение по умолчанию
            # Можно добавить логирование ошибки
            print(f"Ошибка: request is None для NewRecipient с id={recipient.id}")

        # for abonent in recipient.request.abonents.all():
        #     clients.append(abonent.client.client_name)

        context['clients'] = clients
        return context

class NewRecipientCreateView(CreateView):
    model = NewRecipient
    template_name = 'Queue/newrecipient_create.html'
    form_class = NewRecipientForm
    # fields = ['status', 'date', 'receiving_time', 'request', 'note']  # Перечислите поля для формы
    success_url = reverse_lazy('Queue:newrecipient_list')  # URL для перенаправления после успешного создания

    def form_valid(self, form):
        """Заполняем остальные поля на основе выбранного request."""
        logbook_entry = form.cleaned_data['request']
        form.instance.number_naumen = logbook_entry.number_naumen
        form.instance.number_elk = logbook_entry.number_elk
        form.instance.ogv = logbook_entry.ogv
        return super().form_valid(form)

class NewRecipientUpdateView(UpdateView):
    model = NewRecipient
    template_name = 'Queue/newrecipient_update.html'
    # fields = ['status', 'date', 'receiving_time', 'request', 'note']
    form_class = NewRecipientForm
    success_url = reverse_lazy('Queue:newrecipient_list')

    def get_queryset(self):
        return super().get_queryset().select_related('request').prefetch_related(
            Prefetch(
                'request__abonents',
                queryset=NewAbonent.objects.select_related('client')
            )
        )

    def get_object(self, queryset=None):
        """
        Получает объект, который нужно обновить.
        Необходимо для правильной работы UpdateView.
        """
        return get_object_or_404(NewRecipient, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipient = self.get_object()
        clients = []

        try:
            if recipient.request:
                for abonent in recipient.request.abonents.all():
                    clients.append(abonent.client.client_name)
        except AttributeError:
            # Обрабатываем случай, когда request is None
            clients = []  # Или какое-то другое значение по умолчанию
            # Можно добавить логирование ошибки
            print(f"Ошибка: request is None для NewRecipient с id={recipient.id}")

        # for abonent in recipient.request.abonents.all():
        #     clients.append(abonent.client.client_name)

        context['clients'] = clients
        return context

    def get_form_kwargs(self):
        """
        Передает объект в форму.  Это позволяет форме инициализироваться
        данными из существующей модели.
        """
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()  # Передаем экземпляр объекта в форму
        return kwargs

    def get_success_url(self):
        """Redirect to the Logbook's change page in Django Admin."""
        return reverse("admin:Issuance_logbook_change", args=[self.object.request.id])

    def form_valid(self, form):
        self.object = form.save()  # Save the NewRecipient object first
        return super().form_valid(form) # Call the parent class's form_valid method to handle the redirect.

class NewRecipientDeleteView(DeleteView):
    model = NewRecipient
    template_name = 'Queue/newrecipient_delete.html'
    success_url = reverse_lazy('Queue:newrecipient_list')