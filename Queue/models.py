from django.db import models
from  Request.models import NewReq
from Issuance.models import Logbook, Authority
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html

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
        update_logbook = False

        if self.pk is not None:
            old_instance = NewRecipient.objects.get(pk=self.pk)
            if old_instance.status != 'completed' and self.status == 'completed':
                update_logbook = True
        else:
            if self.status == 'completed':
                update_logbook = True

        if self.date and self.status == 'released':
            self.status = 'pending'
        super().save(*args, **kwargs)

        if update_logbook:
            self.update_logbook()

    def update_logbook(self):
        logbook = self.request
        logbook.status = 'received'
        logbook.date_of_receipt = self.date

        # Find the Authority object named "Лично"
        try:
            authority_licno = Authority.objects.get(name="Лично")
            logbook.authority = authority_licno
        except Authority.DoesNotExist:
            # Handle the case where the "Лично" Authority object doesn't exist.
            # You might want to log an error or create the object.
            print("Warning: Authority 'Лично' does not exist!")
            # Optionally create it:
            # authority_licno = Authority.objects.create(name="Лично")
            # logbook.authority = authority_licno

        # Find the maximum log number
        max_log_number = Logbook.objects.exclude(log_number__isnull=True).aggregate(models.Max('log_number'))['log_number__max']
        logbook.log_number = (max_log_number or 0) + 1  # Handle the case where there are no existing log numbers

        logbook.save()

    def logbook_link(self):
        if self.request:
            url = reverse("admin:Issuance_logbook_change", args=[self.request.id])
            return format_html('<a href="{}">{}</a>', url, self.request)
        return None
    logbook_link.short_description = 'Logbook'
