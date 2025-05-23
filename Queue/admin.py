from django.contrib import admin
from .models import NewRecipient


class NewRecipientAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('status', 'date', 'amount', 'ogv')
    # list_display_links = ('date',)
    # list_filter = ('received',)
    date_hierarchy = 'date'
    # search_fields = ('',)
    ordering = ('-status',)

admin.site.register(NewRecipient, NewRecipientAdmin)
