from django.db import models
from django.core.exceptions import ValidationError

# from Request.models import NewReq, Platform, ViPNetNetNumber
from Request.models import NewReq
from Owners.models import NewAbonent, Platform, ViPNetNetNumber
# from Queue.models import NewRecipient


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
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE, verbose_name='Основание', blank=True, null=True)
    number_naumen = models.CharField(max_length=255, verbose_name='Номер Naumen', blank=True, null=True)
    number_elk = models.CharField(max_length=255, verbose_name='Номер ЕЛК', blank=True, null=True)
    ogv = models.TextField(max_length=255, verbose_name='ОГВ')
    amount = models.PositiveIntegerField(verbose_name='dst', default=1)
    abonents = models.ManyToManyField(NewAbonent, verbose_name='Абоненты')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, verbose_name='Платформа')
    net_number = models.ForeignKey(ViPNetNetNumber, on_delete=models.CASCADE, verbose_name='Номер сети')
    note = models.TextField(verbose_name='Примечание', blank=True)

    def __str__(self):
        if self.log_number and self.date_of_receipt:
            if self.number_naumen:
                return f"№ {self.log_number} {self.status} {self.date_of_receipt.strftime('%d.%m.%Y')} по запросу {self.number_naumen} для {self.ogv}, {self.amount} шт."
            else:
                return f"№ {self.log_number} {self.status} {self.date_of_receipt.strftime('%d.%m.%Y')} для {self.ogv}, {self.amount} шт."
        elif self.number_naumen and self.date_of_request:
            return f"№ Б/Н {self.status} по запросу {self.number_naumen} от {self.date_of_request.strftime('%d.%m.%Y')} для {self.ogv}, {self.amount} шт."
        else:
            return f"№ Б/Н {self.status} по запросу для {self.ogv}, {self.amount} шт."
        # return "№ %s выдан %s для %s, %s шт." % (self.log_number, self.date_of_receipt, self.ogv, self.amount)

    # def clean(self):
    #     if int(str(self.amount)) < 1:
    #         raise ValidationError({'amount': "Количество dst должно быть больше 1!"})
    #     if self.abonents.count() != self.amount:
    #         raise ValidationError({'amount': "Количество dst должно совпадать с количеством абонентов."})

    def save(self, *args, **kwargs):
        # Валидация amount перед сохранением
        if self.amount < 1:
            raise ValidationError("Количество dst должно быть больше 1!")

        if self.date_of_receipt and self.status == 'released':
            self.status = 'received'

        # Сначала сохраняем объект, чтобы получить id
        super().save(*args, **kwargs)

        # # Валидация количества абонентов после сохранения и установления связи
        # if self.abonents.count() != self.amount:
        #     print(self.abonents)
        #     print(self.amount)
        #     raise ValidationError({'amount': "Количество dst должно совпадать с количеством абонентов."})

    class Meta:
        ordering = ['-log_number', '-date_of_request', 'status', '-date_of_receipt', '-number_naumen', '-number_elk']
        verbose_name = 'Выдача'
        verbose_name_plural = 'Журнал'