from django.contrib import admin
from .models import Authority, Logbook
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django import forms
from Request.models import NewReq
from Licenses.models import License
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
import unicodedata

class LogbookForm(forms.ModelForm):
    class Meta:
        model = Logbook
        fields = '__all__'
        widgets = {
            'license': forms.Select(attrs={'style': 'min-width: 400px; width: auto;'}),
            'abonents': forms.Select(attrs={'style': 'min-width: 400px; width: auto;'}),
        }

    def __init__(self, *args, **kwargs):
        # get_form в Admin будет передавать сюда request и obj (если мы их добавим)
        request = kwargs.pop('request', None)
        obj = kwargs.pop('obj', None)

        # Важно вызвать базовый конструктор сразу — иначе self.fields не создастся
        super().__init__(*args, **kwargs)

        # Переменная, в которой будем хранить числовой номер сети (int), если удастся получить
        net_value = None

        # 1) Если редактируем существующую запись (change view), берем net_number из obj
        if obj and getattr(obj, 'net_number', None):
            # obj.net_number — это FK на ViPNetNetNumber
            try:
                # берем текстовое поле vipnet_net_number и конвертируем в int
                net_value = int(obj.net_number.vipnet_net_number)
            except (AttributeError, ValueError, TypeError):
                # если что-то не так — оставляем net_value = None
                net_value = None

        # 2) Если форма привязана к POST или есть initial данные (add view или при валидации)
        if net_value is None:
            data = self.data if self.is_bound else self.initial
            if data:
                # в POST/initial поле net_number содержит PK связанного ViPNetNetNumber
                net_pk = data.get('net_number') or data.get('net_number_id')
                if net_pk:
                    try:
                        net_obj = ViPNetNetNumber.objects.filter(pk=net_pk).first()
                        if net_obj:
                            net_value = int(net_obj.vipnet_net_number)
                    except (ValueError, TypeError):
                        net_value = None

        # 3) Устанавливаем queryset для поля license в зависимости от net_value
        if net_value is not None:
            # фильтруем License по целому значению network_number
            self.fields['license'].queryset = License.objects.filter(network_number=net_value)
        else:
            # если номер сети неизвестен (например, при первом открытии формы создания),
            # показываем пустой список, чтобы пользователь сначала выбрал сеть.
            # При желании можно вернуть все лицензии: License.objects.all()
            self.fields['license'].queryset = License.objects.all()

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

@admin.register(Logbook)
class LogbookAdmin(admin.ModelAdmin):
    save_on_top = True
    form = LogbookForm

    autocomplete_fields = ['license', 'abonents']  # включаем автокомплит для поля license

    list_display = (
        'log_number', 'status', 'date_of_request', 'date_of_receipt', 'authority',
        'number_naumen', 'number_elk', 'ogv', 'amount', 'net_number', 'use_license'
    )
    list_display_links = ('log_number',)
    readonly_fields = ('amount',)
    search_fields = (
        'log_number', 'number_naumen', 'number_elk',
        'abonents__owner__full_name', 'abonents__client__client_name', 'ogv'
    )
    list_filter = (
        StatusFilter, 'authority', 'net_number', LogNumberNullFilter,
        NaumenNumberNullFilter, ELKNumberNullFilter, 'use_license'
    )
    date_hierarchy = 'date_of_request'

    def get_form(self, request, obj=None, **kwargs):
        # Получаем стандартный класс формы от ModelAdmin
        Form = super().get_form(request, obj, **kwargs)

        # Оборачиваем его, чтобы в __init__ формы автоматически попадали request и obj
        class FormWithRequest(Form):
            def __init__(self2, *args, **inner_kwargs):
                inner_kwargs.setdefault('request', request)
                inner_kwargs.setdefault('obj', obj)
                super().__init__(*args, **inner_kwargs)

        return FormWithRequest

    def save_model(self, request, obj, form, change):
        """
        При сохранении через админку сначала выполняем валидацию модели (full_clean),
        чтобы показать понятные ошибки пользователю. Затем сохраняем через super().
        Модель Logbook должна в своём save/delete содержать логику изменения License.used.
        """
        try:
            obj.full_clean()
        except ValidationError as e:
            # Показываем сообщение в панели администратора и пробрасываем ошибку,
            # чтобы форма отобразила ошибки.
            messages.error(request, f"Ошибка валидации: {e}")
            # Пробрасываем ValidationError — Django Admin покажет ошибки в форме
            raise
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Перед удалением вызываем obj.delete(), чтобы выполниться логике модели (уменьшение used).
        """
        try:
            obj.delete()
            messages.success(request, "Объект успешно удалён и связанные счетчики обновлены.")
        except Exception as e:
            messages.error(request, f"Ошибка при удалении: {e}")
            raise

    def save_related(self, request, form, formsets, change):
        """
        Оставляем ваше поведение: после сохранения связей обновляем amount.
        """
        super().save_related(request, form, formsets, change)
        try:
            form.instance.update_amount()
        except Exception as e:
            messages.error(request, f"Не удалось обновить поле amount: {e}")

# class LogbookAdmin(admin.ModelAdmin):
#     save_on_top = True
#
#     list_display = ('log_number', 'status', 'date_of_request', 'date_of_receipt', 'authority', 'number_naumen', 'number_elk', 'ogv', 'amount',
#     'net_number', 'use_license', 'license')
#     list_display_links = ('log_number',)
#     readonly_fields = ('amount',)
#     search_fields = ('log_number', 'number_naumen', 'number_elk', 'abonents__owner__full_name', 'abonents__client__client_name', 'ogv')
#     list_filter = (StatusFilter, 'authority', 'net_number', LogNumberNullFilter, NaumenNumberNullFilter, ELKNumberNullFilter, 'use_license')
#     date_hierarchy = 'date_of_request'
#
#     def save_related(self, request, form, formsets, change):
#         super().save_related(request, form, formsets, change)
#         form.instance.update_amount()  # Обновляем amount после сохранения связанных объектов


admin.site.register(Authority)