from django.db.models import Count, Min
from Owners.models import NewAbonent


def remove_duplicate_owners():
    # 1. Укажи поля, по которым запись считается "дубликатом"
    # Например, если у абонентов одинаковый серийный номер и IMEI — это дубль.
    unique_fields = ['owner', 'client']

    # Если нужно искать дубликаты только по одному полю (например, только SN):
    # unique_fields = ['serial number']

    # 2. Находим группы дубликатов
    duplicates = (
        NewAbonent.objects.values(*unique_fields)
        .annotate(count=Count('id'), min_id=Min('id'))
        .filter(count__gt=1)
    )

    print(f"Найдено групп дубликатов: {duplicates.count()}")

    # 3. Удаляем лишние (оставляем только ПОСЛЕДНЮЮ добавленную запись)
    deleted_count = 0
    for dup in duplicates:
        # Формируем фильтр по полям дубликата
        filters = {field: dup[field] for field in unique_fields}

        # Удаляем все записи с этими параметрами, КРОМЕ той, у которой id максимальный (последней)
        count, _ = (
            NewAbonent.objects
            .filter(**filters)
            .exclude(id=dup['min_id'])
            .delete()
        )
        deleted_count += count

    print(f"Готово. Удалено лишних записей: {deleted_count}")

remove_duplicate_owners()