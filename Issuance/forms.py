from django import forms
from .models import Logbook

class ExportLogbookForm(forms.Form):
    selected_ids = forms.CharField(widget=forms.HiddenInput(), required=False)  # Скрытое поле для хранения ID
    export_to_excel = forms.BooleanField(required=False, initial=True, label="Экспортировать в Excel")

    def clean_selected_ids(self):
        data = self.cleaned_data['selected_ids']
        if data:
            try:
                ids = [int(i) for i in data.split(',')]
                return ids
            except ValueError:
                raise forms.ValidationError("Некорректные ID записей.")
        return []
