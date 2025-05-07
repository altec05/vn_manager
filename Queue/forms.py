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
    # date = forms.DateField(
    #     widget=forms.DateInput(format='%d.%m.%Y', attrs={'type': 'date'}),
    #     input_formats=['%d.%m.%Y', '%Y-%m-%d'],
    #     label='Предполагаемая дата получения',
    #     required=False
    # )
    request = forms.ModelChoiceField(
        queryset=Logbook.objects.all(),
        label='Запрос',
        empty_label="Выберите запрос"  # Добавляем пустой вариант
    )

    class Meta:
        model = NewRecipient
        fields = ['status', 'request', 'number_naumen', 'number_elk', 'date', 'receiving_time', 'ogv', 'amount', 'note']
        widgets = {
            'number_naumen': forms.TextInput(attrs={'readonly': 'readonly'}),
            'number_elk': forms.TextInput(attrs={'readonly': 'readonly'}),
            'ogv': forms.Textarea(attrs={'readonly': 'readonly', 'rows': 2}),
            # 'date': DatePickerInput(attrs={'type': 'date'}),  # HTML5 Date Input
            'receiving_time': forms.TimeInput(attrs={'type': 'time'}),  # HTML5 Time Input
            # 'ogv': forms.TextInput(),
            'amount': forms.NumberInput(),
            'note': forms.Textarea(attrs={'rows': 2}),
        }

class RecipientFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'Все статусы'),  # Пустое значение для "всех статусов"
        ('released', 'Выпущено'),
        ('pending', 'Ожидает получателя'),
        ('completed', 'Выдано'),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,  # Необязательное поле
        label='Фильтр',
        initial='pending'
    )