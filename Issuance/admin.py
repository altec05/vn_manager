from django.contrib import admin
from .models import Authority, Logbook
from Request.models import NewReq

class LogbookAdmin(admin.ModelAdmin):
    save_on_top = True

    list_display = ('log_number', 'status', 'date_of_request', 'date_of_receipt', 'authority', 'number_naumen', 'number_elk', 'ogv', 'amount',
    'net_number')
    list_display_links = ('log_number',)
    # readonly_fields = ('date_of_request', 'number_naumen', 'number_elk', 'ogv', 'platform', 'net_number')
    search_fields = ('log_number', 'number_naumen', 'number_elk', 'abonents__owner__full_name', 'abonents__client__client_name')
    list_filter = ('status', 'authority', 'amount', 'net_number')
    date_hierarchy = 'date_of_request'


    # list_display = ('log_number', 'date_of_request', 'date_of_receipt', 'authority', 'number_naumen', 'number_elk', 'ogv', 'amount', 'net_number')
    # list_display_links = ('log_number',)
    # readonly_fields = ('date_of_request', 'number_naumen', 'number_elk', 'ogv', 'platform', 'net_number', 'updated_at', 'workers', 'clients')
    # search_fields = ('log_number', 'number_naumen', 'number_elk', 'abonents__owner__full_name', 'abonents__client__client_name')
    # # list_filter = ('city_of_install',)
    #
    # raw_id_fields = ['zapros', ]
    #
    # # Разделяем абонентов на список сотрудников и список клиентов
    # @staticmethod
    # def get_abonents_str(abonents):
    #     workers = ''
    #     clients = ''
    #     # Проходимся по каждому выбранному абоненту
    #     for abonent in abonents:
    #         # Получаем фио
    #         worker = abonent.owner.full_name
    #         workers += worker + ', '
    #         # Получаем имя клиента
    #         client = abonent.client.client_name
    #         clients += client + ', '
    #     workers = workers.strip()
    #     # Удаляем последнюю запятую
    #     try:
    #         if workers[len(workers)-1] == ',':
    #             workers = workers[:len(workers)-1]
    #     except Exception as e:
    #         print(f'Не удалось убрать запятую для сотрудников: {e}')
    #     clients = clients.strip()
    #     # Удаляем последнюю запятую
    #     try:
    #         if clients[len(clients)-1] == ',':
    #             clients = clients[:len(clients)-1]
    #     except Exception as e:
    #         print(f'Не удалось убрать запятую для клиентов: {e}')
    #     return workers, clients
    #
    #
    # def save_model(self, request, obj, form, change):
    #     if form.is_valid():
    #         for req in NewReq.objects.all():
    #             if obj.zapros.number_naumen:
    #                 if req.number_naumen == obj.zapros.number_naumen:
    #                     obj.date_of_request = req.date
    #                     obj.number_naumen = req.number_naumen
    #                     obj.number_elk = req.number_elk
    #                     obj.platform = req.platform
    #                     obj.net_number = req.net_number
    #                     obj.ogv = req.ogv
    #                     # obj.amount = req.amount
    #                     try:
    #                         workers, clients = self.get_abonents_str(obj.abonents.all())
    #                         obj.workers = workers
    #                         obj.clients = clients
    #                     except Exception as e:
    #                         print(f'Не удалось разобрать абонентов: {e}.\nПовторите попытку!')
    #         obj.save()
    #     else:
    #         print('Форма не валид!')

admin.site.register(Authority)
admin.site.register(Logbook, LogbookAdmin)