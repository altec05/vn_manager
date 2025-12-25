from django.contrib import admin
from .models import Authority, Logbook
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django import forms
from Request.models import NewReq
from Licenses.models import License
from Queue.models import NewRecipient
from Owners.models import ViPNetNetNumber
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
import unicodedata

class LogbookForm(forms.ModelForm):
    class Meta:
        model = Logbook
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        obj = kwargs.pop('obj', None)

        super().__init__(*args, **kwargs)

        net_value = None
        platform = None

        # 1) Если редактируем существующую запись (change view)
        if obj:
            if getattr(obj, 'net_number', None):
                try:
                    net_value = int(obj.net_number.vipnet_net_number)
                except (AttributeError, ValueError, TypeError):
                    pass
            if getattr(obj, 'platform', None):
                try:
                    platform_name = obj.platform.platform_name
                    if platform_name == 'Android (Планшет)' or platform_name == 'Android (Мобильный клиент)':
                        platform = 'Android'
                    elif platform_name == 'Windows':
                        platform = 'Windows'
                    else:
                        platform = platform_name # или None, если другие не нужны
                except (AttributeError, ValueError, TypeError):
                    pass

        # 2) Если форма привязана к POST или есть initial данные (add view или при валидации)
        if net_value is None: # Если не удалось получить из obj, пробуем из данных
            data = self.data if self.is_bound else self.initial
            if data:
                net_pk = data.get('net_number') or data.get('net_number_id')
                if net_pk:
                    try:
                        net_obj = ViPNetNetNumber.objects.filter(pk=net_pk).first()
                        if net_obj:
                            net_value = int(net_obj.vipnet_net_number)
                    except (ValueError, TypeError):
                        pass

        # 3) Устанавливаем queryset для поля license
        if net_value is not None:
            network_filter_condition = Q(network_number=net_value)
            if platform == 'Android':
                license_filter_condition = Q(license_object__icontains="Android")
                combined_filter = network_filter_condition & license_filter_condition
                self.fields['license'].queryset = License.objects.filter(combined_filter)
            elif platform == 'Windows':
                license_filter_condition = Q(license_object__icontains="Windows")
                combined_filter = network_filter_condition & license_filter_condition
                self.fields['license'].queryset = License.objects.filter(combined_filter)
            else:
                self.fields['license'].queryset = License.objects.filter(network_number=net_value)
        else:
            # Если номер сети неизвестен, можно либо показать пустой queryset, либо все лицензии.
            # Сейчас показаны все, но лучше фильтровать после выбора сети.
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

    # inlines = [NewRecipientInline,]

    # autocomplete_fields = ['license', 'abonents']  # включаем автокомплит для поля license
    autocomplete_fields = ['abonents',]

    class Media:
        css = {
            'all': ('Issuance/css/admin_overrides.css',)
        }

    list_display = (
        'log_number', 'use_license', 'status', 'date_of_request', 'date_of_receipt', 'authority',
        'number_naumen', 'number_elk', 'ogv', 'amount', 'net_number'
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

        Сохраняем объект и после этого обновляем абонентов,
        а также показываем информационное сообщение.
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

        # Теперь обновляем абонентов и считаем, сколько затронуто
        updated_count = 0
        if obj.abonents.exists():
            for abonent in obj.abonents.all():
                updated = False
                if not abonent.net_number:
                    abonent.net_number = obj.net_number
                    updated = True
                if not abonent.platform:
                    abonent.platform = obj.platform
                    updated = True
                if updated:
                    abonent.save()
                    updated_count += 1

                    # Показываем сообщение, если были обновления
                    if updated_count > 0:
                        if updated_count == 1:
                            message = "Обновлён 1 абонент: заполнены поля «Сеть» и «Платформа»."
                        elif updated_count < 5:
                            message = f"Обновлены {updated_count} абонента: заполнены поля «Сеть» и «Платформа»."
                        else:
                            message = f"Обновлено {updated_count} абонентов: заполнены поля «Сеть» и «Платформа»."
                        messages.info(request, message)
                    else:
                        # Можно не показывать, или показать, что всё уже было заполнено
                        messages.info(request, "Абоненты уже имели заполненные поля «Сеть» и «Платформа». Поля абонентов не были обновлены.")
                        # pass
                else:
                    messages.info(request, "Абоненты уже имели заполненные поля «Сеть» и «Платформа». Поля абонентов не были обновлены.")


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