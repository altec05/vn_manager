from django.db import models
from django.core.exceptions import ValidationError


class ViPNetNetNumber(models.Model):
    vipnet_net_number = models.CharField(max_length=5, verbose_name='Номер сети', unique=True)
    vipnet_net_description = models.CharField(max_length=255, verbose_name='Описание сети')

    def clean(self):
        if not str(self.vipnet_net_number).isdigit():
            raise ValidationError({'vipnet_net_number': "Номер сети ViPNet должен содержать только цифры!"})

    def __str__(self):
        return f'{ self.vipnet_net_number} - {self.vipnet_net_description}'

    class Meta:
        ordering = ['vipnet_net_number']
        verbose_name = 'ViPNet сеть'
        verbose_name_plural = 'ViPNet сети'


class Platform(models.Model):
    platform_name = models.CharField(max_length=255, verbose_name='Наименование', unique=True)

    def __str__(self):
        return self.platform_name

    class Meta:
        ordering = ['platform_name']
        verbose_name = 'Платформа'
        verbose_name_plural = 'Платформы'


class ClientName(models.Model):
    client_name = models.CharField(max_length=255, verbose_name='Наименование клиента')

    def __str__(self):
        return self.client_name

    class Meta:
        ordering = ['client_name']
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Owner(models.Model):
    full_name = models.CharField(max_length=255, verbose_name='ФИО полностью', unique=True)

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ['full_name']
        verbose_name = 'Владелец'
        verbose_name_plural = 'Владельцы'

    def clean(self):
        if str(self.full_name).count(' ') < 2:
            raise ValidationError({'full_name': "Укажите полное ФИО!"})

class NewAbonent(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.PROTECT, verbose_name='ФИО владельца')
    client = models.ForeignKey(ClientName, on_delete=models.PROTECT, verbose_name='Клиент')
    net_number = models.ForeignKey(ViPNetNetNumber, on_delete=models.PROTECT, verbose_name='Сеть', null=True, blank=True)
    identifier = models.CharField(max_length=255, verbose_name='ID узла', blank=True)
    ogv = models.CharField(max_length=255, verbose_name='Организация', blank=True)
    platform = models.ForeignKey(Platform, on_delete=models.PROTECT, verbose_name='Платформа', null=True, blank=True)
    serial_number = models.CharField(max_length=255, verbose_name='S/N', blank=True)
    imei = models.TextField(max_length=255, verbose_name='IMEI', blank=True)
    iccid = models.CharField(max_length=255, verbose_name='ICCID', blank=True)
    active = models.BooleanField(default=True, verbose_name='Активный')
    note = models.TextField(verbose_name='Примечание', blank=True)


    def __str__(self):
        return self.owner.full_name + ' - (' + self.client.client_name + ')'

    class Meta:
        ordering = ['client', 'owner', 'ogv']
        verbose_name = 'Абонент'
        verbose_name_plural = 'Абоненты'
        unique_together = ('owner', 'client')