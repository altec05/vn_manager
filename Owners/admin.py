from django import forms
from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect
from .models import Owner, ClientName, NewAbonent, ViPNetNetNumber, Platform


class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(label="Файл .xlsx")

# @admin.register(NewAbonent)
class NewAbonentAdmin(admin.ModelAdmin):
    autocomplete_fields = ['owner', 'client']
    list_display = ('client', 'owner', 'ogv', 'active')
    list_display_links = ('client',)
    search_fields = ('owner__full_name', 'client__client_name', 'ogv', 'serial_number', 'imei', 'iccid', 'note', 'identifier')
    list_filter = ('active', 'platform', 'net_number', 'ogv')
    save_on_top = True

    change_list_template = 'admin/Owners/change_list_import_button.html'  # Добавьте эту строку

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
    search_fields = ('full_name',)

@admin.register(ClientName)
class ClientNameAdmin(admin.ModelAdmin):
    list_display = ('client_name',)
    search_fields = ('client_name',)

admin.site.register(Platform)
admin.site.register(ViPNetNetNumber)
admin.site.register(NewAbonent, NewAbonentAdmin)
