# Queue/templatetags/pagination_tags.py
from django import template

register = template.Library()

@register.simple_tag
def get_page_list(page_obj, left=2, right=2):
    """
    Возвращает список чисел страниц и None для троеточия.
    left/right — сколько страниц слева/справа от текущей показывать.
    Пример: [1, None, 5, 6, 7, None, 20]
    """
    paginator = page_obj.paginator
    current = page_obj.number
    total = paginator.num_pages

    if total <= 1:
        return [1]

    pages = [1]

    start = max(2, current - left)
    end = min(total - 1, current + right)

    if start > 2:
        pages.append(None)

    for p in range(start, end + 1):
        pages.append(p)

    if end < total - 1:
        pages.append(None)

    if total > 1:
        pages.append(total)

    return pages