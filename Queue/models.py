from django.db import models
from  Request.models import NewReq
from Issuance.models import Logbook
from django.core.exceptions import ValidationError

class NewRecipient(models.Model):
    STATUS_CHOICES = [
        ('released', 'Выпущено'),
        ('pending', 'Ожидает получателя'),
        ('completed', 'Выдано'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    number_naumen = models.CharField(max_length=255, verbose_name='Номер Naumen', blank=True, null=True)
    number_elk = models.CharField(max_length=255, verbose_name='Номер ЕЛК', blank=True, null=True)
    date = models.DateField(verbose_name='Предполагаемая дата получения', blank=True, null=True)
    receiving_time = models.TimeField(verbose_name='Время получения', blank=True, null=True)
    ogv = models.TextField(max_length=255, verbose_name='Заявитель', blank=True, null=True)
    amount = models.PositiveIntegerField(verbose_name='Всего dst', default=1)
    # request = models.ForeignKey(NewReq, on_delete=models.CASCADE, verbose_name='Запрос')
    request = models.ForeignKey(Logbook, on_delete=models.CASCADE, verbose_name='Запрос')
    # received = models.BooleanField(default=False, verbose_name='Получено')
    note = models.TextField(verbose_name='Примечание', blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Запись на получение'
        verbose_name_plural = 'Записи на получение'

    def __str__(self):
        return f"{self.status} - {self.date} - {self.amount} - {self.ogv}"

    def clean(self):
        if int(str(self.amount)) < 1:
            raise ValidationError({'amount': "Количество dst должно быть больше 1!"})

    def save(self, *args, **kwargs):
        if self.date and self.status == 'released':
            self.status = 'pending'
        super().save(*args, **kwargs)
