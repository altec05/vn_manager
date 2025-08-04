# Queue/templatetags/queue_extras.py
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='display_recipient_status')
def display_recipient_status(recipient):
    """
    Форматирует отображение статуса получателя.
    """
    status_display = recipient.get_status_display()
    if recipient.status == 'completed':
        status_display += f"<br>№ - {recipient.request.log_number}"  # Передаем функцию с форматированием, чтобы был указан № в журнале
    return status_display