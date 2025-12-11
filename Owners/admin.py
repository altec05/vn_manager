from django.contrib import admin
from .models import ClientName, Owner, NewAbonent, Platform, ViPNetNetNumber


@admin.register(NewAbonent)
class NewAbonentAdmin(admin.ModelAdmin):
    autocomplete_fields = ['owner', 'client']
    list_display = ('owner', 'client')
    search_fields = ('owner__full_name', 'client__client_name')
    save_on_top = True

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
