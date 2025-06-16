from django.contrib import admin
from .models import NewRecipient
from django.utils.html import format_html
from django.urls import reverse


class NewRecipientAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('status', 'date', 'amount', 'request_link', 'ogv')
    # list_display_links = ('date',)
    # list_filter = ('received',)
    date_hierarchy = 'date'
    # search_fields = ('',)
    ordering = ('-status',)

    def request_link(self, obj):
        if obj.request:
            url = reverse("admin:Issuance_logbook_change", args=[obj.request.pk])  # Replace 'Issuance' if needed
            link_text = obj.request.number_naumen or "N/A"  # Use number_naumen, default to "N/A" if None
            return format_html('<a href="{}">{}</a>'.format(url, link_text))
        return None
    request_link.short_description = 'Запрос'  # Column header in admin
    request_link.admin_order_field = 'request'  # Allows sorting by the request field

    readonly_fields = ('request_link',)  # Make the field read-only so it's not editable in the admin

    def get_readonly_fields(self, request, obj=None):
        if obj:  # This is an edit, not a create
            return self.readonly_fields
        else:
            return () # Don't make request_link readonly on creation

admin.site.register(NewRecipient, NewRecipientAdmin)
