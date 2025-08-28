from django import forms
from .models import NewRecipient
from Issuance.models import Logbook
from bootstrap_datepicker_plus.widgets import DatePickerInput

class NewRecipientForm(forms.ModelForm):
    date = forms.DateField(
        widget=DatePickerInput(options={
                   "format": "DD.MM.YYYY",  # Формат даты
                   "locale": "ru"           # Локализация на русский
               }),
        label='Предполагаемая дата получения',
        required=False
    )
    objs = Logbook.objects.filter(log_number__isnull=True)
    if len(objs) < 1:
        objs = Logbook.objects.all()
    request = forms.ModelChoiceField(
        queryset=objs,
        # queryset=Logbook.objects.all(),
        label='Запрос',
        empty_label="Выберите запрос"  # Добавляем пустой вариант
    )

    class Meta:
        model = NewRecipient
        fields = ['status', 'request', 'number_naumen', 'number_elk', 'date', 'receiving_time', 'ogv', 'amount', 'note']

        widgets = {
            'number_naumen': forms.TextInput(attrs={'readonly': 'readonly'}),
            'number_elk': forms.TextInput(attrs={'readonly': 'readonly'}),
            'ogv': forms.Textarea(attrs={'readonly': 'readonly', 'rows': 1}),
            # 'date': DatePickerInput(attrs={'type': 'date'}),  # HTML5 Date Input
            'receiving_time': forms.TimeInput(attrs={'type': 'time'}),  # HTML5 Time Input
            # 'ogv': forms.TextInput(),
            'amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'note': forms.Textarea(attrs={'rows': 2}),
        }
        help_texts = {
            'number_naumen': 'Поле будет заполнено из запроса после сохранения!',
            'number_elk': 'Поле будет будет заполнено из запроса после сохранения!',
            'ogv': 'Поле будет будет заполнено из запроса после сохранения!',
            'amount': 'Поле будет будет заполнено из запроса после сохранения!',
        }

class RecipientFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'Все статусы'),  # Пустое значение для "всех статусов"
        ('released', 'Выпущено'),
        ('pending', 'Ожидает получателя'),
        ('not_completed', 'Не выдано'),
        ('completed', 'Выдано'),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,  # Необязательное поле
        label='Фильтр',
        initial='not_completed'
    )