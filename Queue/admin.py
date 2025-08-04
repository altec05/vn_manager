from django.contrib import admin
from .models import NewRecipient
from django.utils.html import format_html, format_html_join
from django.urls import reverse
from django.utils.safestring import mark_safe


class NewRecipientAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('status', 'date', 'amount', 'request_link', 'ogv', 'get_log_number', 'get_abonent_name', 'get_clients', 'created_at')
    # list_display_links = ('date',)
    list_filter = ('status',)
    date_hierarchy = 'date'
    # search_fields = ('',)
    ordering = ('-created_at',)

    def request_link(self, obj):
        if obj.request:
            url = reverse("admin:Issuance_logbook_change", args=[obj.request.pk])  # Replace 'Issuance' if needed
            link_text = obj.request.number_naumen or "N/A"  # Use number_naumen, default to "N/A" if None
            return format_html('<a href="{}">{}</a>'.format(url, link_text))
        return None
    request_link.short_description = 'Запрос'  # Column header in admin
    request_link.admin_order_field = 'request'  # Allows sorting by the request field

    readonly_fields = ('request_link', 'created_at', 'get_log_number', 'get_clients', 'get_abonent_name')  # Make the field read-only so it's not editable in the admin

    def get_log_number(self, obj):
        return obj.request.log_number if obj.request else None  # Получаем значение, если request существует

    get_log_number.short_description = '№ в журнале'

    def get_clients(self, obj):
        return mark_safe(
            "<br>".join(
                [f"{client.client.client_name}" for client in obj.request.abonents.all()]
            )
        )

    get_clients.short_description = 'Клиенты'

    def get_abonent_name(self, obj):
        return mark_safe(
            "<br>".join(
                [f"{abonent.owner.full_name}" for abonent in obj.request.abonents.all()]
            )
        )

    get_abonent_name.short_description = 'Абоненты'

    def get_readonly_fields(self, request, obj=None):
        if obj:  # This is an edit, not a create
            return self.readonly_fields
        else:
            return () # Don't make request_link readonly on creation

admin.site.register(NewRecipient, NewRecipientAdmin)
