from django.contrib import admin
from .models import NewRecipient


class NewRecipientAdmin(admin.ModelAdmin):
    save_on_top = True
    # list_display = ('date', 'request')
    # list_display_links = ('date',)
    # list_filter = ('received',)
    date_hierarchy = 'date'
    # search_fields = ('',)
    # ordering = ('status', 'publish')

admin.site.register(NewRecipient, NewRecipientAdmin)
