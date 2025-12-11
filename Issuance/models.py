from django.db import models
from django.core.exceptions import ValidationError

# from Request.models import NewReq, Platform, ViPNetNetNumber
from Request.models import NewReq
from Owners.models import NewAbonent, Platform, ViPNetNetNumber
from Licenses.models import License

class Authority(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Основание'
        verbose_name_plural = 'Основания'


class Logbook(models.Model):
    STATUS_CHOICES = [
        ('not_released', 'Заявка'),
        ('released', 'Подготовлен'),
        ('received', 'Выдан'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_released',
        verbose_name='Статус'
    )
    # zapros = models.ForeignKey(NewReq, on_delete=models.CASCADE, verbose_name='По запросу')
    log_number = models.PositiveIntegerField(verbose_name='№ в журнале', blank=True, null=True)
    date_of_request = models.DateField(verbose_name='Дата запроса', blank=True, null=True)
    date_of_receipt = models.DateField(verbose_name='Дата получения', blank=True, null=True)
    authority = models.ForeignKey(Authority, on_delete=models.PROTECT, verbose_name='Основание', blank=True, null=True)
    number_naumen = models.CharField(max_length=255, verbose_name='Номер Naumen', blank=True, null=True)
    number_elk = models.CharField(max_length=255, verbose_name='Номер ЕЛК', blank=True, null=True)
    ogv = models.TextField(max_length=255, verbose_name='ОГВ')
    amount = models.PositiveIntegerField(verbose_name='dst', default=1)
    abonents = models.ManyToManyField(NewAbonent, verbose_name='Абоненты')
    platform = models.ForeignKey(Platform, on_delete=models.PROTECT, verbose_name='Платформа')
    net_number = models.ForeignKey(ViPNetNetNumber, on_delete=models.PROTECT, verbose_name='Номер сети')
    note = models.TextField(verbose_name='Примечание', blank=True)
    use_license = models.BooleanField(verbose_name='Используется лицензия', default=False)
    license = models.ForeignKey(License, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Лицензия')

    def __str__(self):
        if self.log_number and self.date_of_receipt:
            if self.number_naumen:
                return f"№ {self.log_number} {self.get_status_display()} {self.date_of_receipt.strftime('%d.%m.%Y')} по запросу {self.number_naumen} для {self.ogv}, {self.amount} шт."
            else:
                return f"№ {self.log_number} {self.get_status_display()} {self.date_of_receipt.strftime('%d.%m.%Y')} для {self.ogv}, {self.amount} шт."
        elif self.number_naumen and self.date_of_request:
            return f"№ Б/Н {self.get_status_display()} по запросу {self.number_naumen} от {self.date_of_request.strftime('%d.%m.%Y')} для {self.ogv}, {self.amount} шт."
        elif self.number_naumen:
            return f"№ Б/Н {self.get_status_display()} по запросу {self.number_naumen} от ___ для {self.ogv}, {self.amount} шт."
        else:
            return f"№ Б/Н {self.get_status_display()} по запросу для {self.ogv}, {self.amount} шт."

    def clean(self):
        # Проверяем согласованность полей use_license и license
        from django.core.exceptions import ValidationError
        if self.use_license and not self.license:
            raise ValidationError(
                {'license': 'Если отмечено "Используется лицензия", необходимо указать ссылку на объект Лицензия.'})
        if not self.use_license and self.license:
            raise ValidationError({'license': 'Если "Используется лицензия" = Нет, поле лицензии должно быть пустым.'})

    def save(self, *args, **kwargs):
        # Сначала проверка согласованности
        self.full_clean()

        # Чтобы корректно обновлять счётчик использованных лицензий, учтём старое состояние
        old = None
        if self.pk:
            try:
                old = Logbook.objects.get(pk=self.pk)
            except Logbook.DoesNotExist:
                old = None

        # Сохраняем модель (пока) — но сначала правильно скорректируем объекты License
        # Подход:
        # - Если старого объекта не было: при создании, если есть license и use_license=True -> прибавить amount
        # - Если старый был:
        #    * если license не изменился: delta = self.amount - old.amount; изменить license.used += delta
        #    * если license изменился: вычесть old.amount из old.license.used (если был), добавить self.amount к новой license.used (если указан)

        # Обрабатываем уменьшение в старой лицензии (если сменили лицензию или удаляем)
        if old:
            # если у старого была привязка к лицензии, вычитаем старое значение
            if old.license:
                old_license = old.license
                # безопасно вычислим
                old_license.used = max(0, (old_license.used or 0) - (old.amount or 0))
                old_license.save()

        # Теперь, если текущий объект использует лицензию, добавим amount к текущей license.used
        if self.use_license and self.license:
            self.license.used = (self.license.used or 0) + (self.amount or 0)
            self.license.save()

        # Если use_license == False, но ранее была лицензия — уже обработали вычитание выше

        # Наконец сохраняем сам Logbook
        super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     if self.date_of_receipt and self.status == 'released':
    #         self.status = 'received'
    #
    #     # Сначала сохраняем объект, чтобы получить id
    #     super().save(*args, **kwargs)

    def update_amount(self):
        self.amount = self.abonents.count()
        self.save(update_fields=['amount'])

    def delete(self, *args, **kwargs):
        # перед удалением скорректируем поле used в лицензии, если есть связь
        if self.license:
            lic = self.license
            lic.used = max(0, (lic.used or 0) - (self.amount or 0))
            lic.save()
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-log_number', '-date_of_request', 'status', '-date_of_receipt', '-number_naumen', '-number_elk']
        verbose_name = 'Выдача'
        verbose_name_plural = 'Журнал'