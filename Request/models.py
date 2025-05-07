from django.db import models
import datetime
from django.core.exceptions import ValidationError

from Owners.models import Owner, Platform, ViPNetNetNumber, NewAbonent


class NewReq(models.Model):
    date = models.DateField(verbose_name='Дата запроса')
    number_naumen = models.CharField(max_length=255, verbose_name='Номер Naumen', blank=True)
    number_elk = models.CharField(max_length=255, verbose_name='Номер ЕЛК', blank=True)
    ogv = models.CharField(max_length=255, verbose_name='ОГВ')
    amount = models.PositiveIntegerField(verbose_name='dst', default=1)
    # owners = models.ForeignKey(Owner, on_delete=models.CASCADE, verbose_name='Владельцы')
    # owners = models.ManyToManyField(Owner, verbose_name='Получатели', blank=True, null=True)
    abonents = models.ManyToManyField(NewAbonent, verbose_name='Абоненты')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, verbose_name='Платформа')
    net_number = models.ForeignKey(ViPNetNetNumber, on_delete=models.CASCADE, verbose_name='Номер сети')
    # released = models.BooleanField(default=False, verbose_name='Выпущено', blank=True)
    # date_of_release = models.DateField(verbose_name='Дата выпуска', blank=True, null=True)
    note = models.TextField(verbose_name='Примечание', blank=True)

    def __str__(self):
        out = f'{self.date} - '
        if self.number_naumen:
            out += str(self.number_naumen) + ' - '
        if self.number_elk:
            out += 'ЕЛК ' +  str(self.number_elk) + ', '
        out += f'{self.ogv}, {self.amount} шт.'
        return out

    def clean(self):
        if not str(self.amount).isdigit():
            raise ValidationError({'amount': "dst должен содержать только цифры!"})
        if int(str(self.amount)) < 1:
            raise ValidationError({'amount': "Количество dst должно быть больше 1!"})

    class Meta:
        ordering = ['date', 'number_naumen', 'number_elk', 'ogv', 'amount', 'net_number']
        verbose_name = 'Запрос'
        verbose_name_plural = 'Запросы'




