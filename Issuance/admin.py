from django.contrib import admin
from .models import Authority, Logbook
from Request.models import NewReq
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
import unicodedata

class StatusFilter(admin.SimpleListFilter):
    title = _('Статус')  # Отображаемое имя фильтра
    parameter_name = 'status'  # Имя параметра в URL

    def lookups(self, request, model_admin):
        return (
            ('not_released', _('Заявка')),  # Отображаемое имя для "Пусто"
            ('released', _('Подготовлен')),  # Отображаемое имя для "Не пусто"
            ('not_received', _('Не выдан')),  # Отображаемое имя для "Пусто"
            ('received', _('Выдан')),  # Отображаемое имя для "Не пусто"
        )

    def queryset(self, request, queryset):
        if self.value() == 'not_released':
            return queryset.filter(status__iexact='not_released')  # Фильтруем по статусу Заявка
        elif self.value() == 'released':
            return queryset.filter(status__iexact='released')  # Фильтруем по статусу Подготовлен
        elif self.value() == 'received':
            return queryset.filter(status__iexact='received')  # Фильтруем по статусу Выдан
        elif self.value() == 'not_received':
            return queryset.exclude(status__iexact='received')  # Фильтруем по статусу, кроме Выдан
        return queryset

class LogNumberNullFilter(admin.SimpleListFilter):
    title = _('Номер в журнале')  # Отображаемое имя фильтра
    parameter_name = 'log_number_null'  # Имя параметра в URL

    def lookups(self, request, model_admin):
        return (
            ('yes', _('-')),  # Отображаемое имя для "Пусто"
            ('no', _('№')),  # Отображаемое имя для "Не пусто"
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(log_number__isnull=True)  # Фильтруем по null
        if self.value() == 'no':
            return queryset.filter(log_number__isnull=False)  # Фильтруем по не null
        return queryset

class NaumenNumberNullFilter(admin.SimpleListFilter):
    title = _('Номер Naumen')  # Отображаемое имя фильтра
    parameter_name = 'number_naumen_null'  # Имя параметра в URL

    def lookups(self, request, model_admin):
        return (
            ('yes', _('-')),  # Отображаемое имя для "Пусто"
            ('no', _('RP')),  # Отображаемое имя для "Не пусто"
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(number_naumen__isnull=True)  # Фильтруем по null
        if self.value() == 'no':
            return queryset.filter(number_naumen__isnull=False)  # Фильтруем по не null
        return queryset

class ELKNumberNullFilter(admin.SimpleListFilter):
    title = _('Номер ЕЛК')  # Отображаемое имя фильтра
    parameter_name = 'number_elk_null'  # Имя параметра в URL

    def lookups(self, request, model_admin):
        return (
            ('yes', _('-')),  # Отображаемое имя для "Пусто"
            ('no', _('#')),  # Отображаемое имя для "Не пусто"
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(number_elk__isnull=True)  # Фильтруем по null
        if self.value() == 'no':
            return queryset.filter(number_elk__isnull=False)  # Фильтруем по не null
        return queryset


class LogbookAdmin(admin.ModelAdmin):
    save_on_top = True

    list_display = ('log_number', 'status', 'date_of_request', 'date_of_receipt', 'authority', 'number_naumen', 'number_elk', 'ogv', 'amount',
    'net_number')
    list_display_links = ('log_number',)
    readonly_fields = ('amount',)
    search_fields = ('log_number', 'number_naumen', 'number_elk', 'abonents__owner__full_name', 'abonents__client__client_name', 'ogv')
    list_filter = (StatusFilter, 'authority', 'net_number', LogNumberNullFilter, NaumenNumberNullFilter, ELKNumberNullFilter)
    date_hierarchy = 'date_of_request'


admin.site.register(Authority)
admin.site.register(Logbook, LogbookAdmin)