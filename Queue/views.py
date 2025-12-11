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
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Создаем изменяемую копию GET-параметров
        form_data = self.request.GET.copy()

        # Если параметр 'status' отсутствует в GET-запросе,
        # устанавливаем его значение по умолчанию 'not_completed'.
        # Это сработает при первом открытии страницы (без GET-параметров)
        # и при пагинации, если пользователь ранее не выбирал другой фильтр.
        if 'status' not in form_data:
            form_data['status'] = 'not_completed'

        # Инициализируем форму с нашей (возможно, модифицированной) копией GET-параметров
        self.form = RecipientFilterForm(form_data)

        if self.form.is_valid():
            status = self.form.cleaned_data.get('status')

            if status == 'not_completed':
                queryset = queryset.exclude(status='completed')
            elif status and status != '':  # '' означает, что фильтр по статусу не применяется
                queryset = queryset.filter(status=status)
            # Если status == '', то никаких дополнительных фильтров по статусу не применяется,
            # и queryset остается базовым (или уже отфильтрованным по другим параметрам, если они есть).

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.form  # Передайте форму в шаблон

        # Получаем номер текущей страницы
        page_number = self.request.GET.get('page', 1)
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 1

        # Вычисляем начальный номер строки
        start_row_number = (page_number - 1) * self.paginate_by + 1
        context['start_row_number'] = start_row_number

        # Добавляем словарь с классами статусов в контекст
        context['status_classes'] = {
            'released': 'status-released',
            'pending': 'status-pending',
            'completed': 'status-completed',
        }
        return context

# class NewRecipientListView(ListView):
#     model = NewRecipient
#     template_name = 'Queue/newrecipient_list.html'
#     context_object_name = 'recipients'
#     paginate_by = 10  # Добавьте пагинацию, если нужно
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#
#         self.form = RecipientFilterForm(self.request.GET)  # Всегда инициализируем форму с GET-параметрами
#
#         if self.form.is_valid():
#             status = self.form.cleaned_data.get('status')
#
#             if status == 'not_completed':
#                 queryset = queryset.exclude(status='completed')
#             elif status and status != 'all':  # Добавим проверку на 'all' если он есть в форме
#                 queryset = queryset.filter(status=status)
#         elif not self.request.GET:  # Если GET-параметров нет (первый вход)
#             # Применяем фильтр "Не выдано" по умолчанию
#             queryset = queryset.exclude(status='completed')
#             self.form = RecipientFilterForm(
#                 initial={'status': 'not_completed'})  # Устанавливаем начальное значение в форме
#
#         # #  При первом открытии страницы применяем фильтр "Не выдано"
#         # if not self.request.GET:
#         #     queryset = queryset.exclude(status='completed')
#         #     self.form = RecipientFilterForm(initial={'status': 'not_completed'})  # Фильтр при загрузке страницы
#         # else:
#         #     self.form = RecipientFilterForm(self.request.GET)
#         #     if self.form.is_valid():
#         #         status = self.form.cleaned_data.get('status')
#         #
#         #         if status == 'not_completed':
#         #             queryset = queryset.exclude(status='completed')
#         #         elif status:
#         #             queryset = queryset.filter(status=status)
#
#         return queryset
#
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['filter_form'] = self.form  # Передайте форму в шаблон
#
#         # Получаем номер текущей страницы
#         page_number = self.request.GET.get('page', 1)  # Используем get с дефолтным значением
#         try:
#             page_number = int(page_number)
#         except ValueError:
#             page_number = 1
#
#         # Вычисляем начальный номер строки
#         start_row_number = (page_number - 1) * self.paginate_by + 1
#         context['start_row_number'] = start_row_number
#
#         # Добавляем словарь с классами статусов в контекст
#         context['status_classes'] = {
#             'released': 'status-released',
#             'pending': 'status-pending',
#             'completed': 'status-completed',
#         }
#         return context

class NewRecipientDetailView(DetailView):
    model = NewRecipient
    template_name = 'Queue/newrecipient_detail.html'
    context_object_name = 'recipient'

    def get_queryset(self):
        # Оптимизируем запрос
        return super().get_queryset().select_related('request').prefetch_related(
            Prefetch(
                'request__abonents',
                queryset=NewAbonent.objects.select_related('client', 'owner')  # Оптимизируем связь NewAbonent с Client
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipient = self.get_object()
        clients = []
        abonents = []
        platform = recipient.request.platform

        try:
            if recipient.request:
                for abonent in recipient.request.abonents.all():
                    clients.append(abonent.client.client_name)
                    abonents.append(abonent.owner.full_name)
        except AttributeError:
            # Обрабатываем случай, когда request is None
            clients = []  # Или какое-то другое значение по умолчанию
            abonents = []
            # Можно добавить логирование ошибки
            print(f"Ошибка: request is None для NewRecipient с id={recipient.id}")

        context['clients'] = clients
        context['abonents'] = abonents
        context['platform'] = platform
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
        form.instance.amount = logbook_entry.amount

        return super().form_valid(form)

class NewRecipientUpdateView(UpdateView):
    model = NewRecipient
    template_name = 'Queue/newrecipient_update.html'
    form_class = NewRecipientForm
    success_url = reverse_lazy('Queue:newrecipient_list')

    def get_queryset(self):
        return super().get_queryset().select_related('request').prefetch_related(
            Prefetch(
                'request__abonents',
                queryset=NewAbonent.objects.select_related('client', 'owner')
            )
        )

    def get_object(self, queryset=None):
        return get_object_or_404(NewRecipient, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipient = self.get_object()
        clients = []
        abonents = []
        platform = recipient.request.platform


        try:
            if recipient.request:
                for abonent in recipient.request.abonents.all():
                    clients.append(abonent.client.client_name)
                    abonents.append(abonent.owner.full_name)
        except AttributeError:
            clients = []
            abonents = []
            print(f"Ошибка: request is None для NewRecipient с id={recipient.id}")

        context['clients'] = clients
        context['abonents'] = abonents
        context['platform'] = platform
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

    def form_valid(self, form):
        instance = self.get_object()
        old_status = instance.status
        new_recipient = form.save(commit=False)  # Сохраняем форму, но не коммитим изменения в базу данных сразу

        # Всегда обновляем поля из request, если request существует
        if new_recipient.request:
            logbook_entry = new_recipient.request
            new_recipient.number_naumen = logbook_entry.number_naumen
            new_recipient.number_elk = logbook_entry.number_elk
            new_recipient.ogv = logbook_entry.ogv
            new_recipient.amount = logbook_entry.amount

        new_recipient.save()  # Сохраняем изменения в базе данных

        if old_status != 'completed' and new_recipient.status == 'completed':
            self.success_url = reverse("admin:Issuance_logbook_change", args=[new_recipient.request.id])
        else:
            self.success_url = reverse_lazy('Queue:newrecipient_list')

        return super().form_valid(form)

class NewRecipientDeleteView(DeleteView):
    model = NewRecipient
    template_name = 'Queue/newrecipient_delete.html'
    success_url = reverse_lazy('Queue:newrecipient_list')