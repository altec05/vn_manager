from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import F  # Импортируем F для более эффективных обновлений
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

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
            return f"№ Б/Н {self.get_status_display()} для {self.ogv}, {self.amount} шт."

    def clean(self):
        print(f'self.use_license - {self.use_license}\nself.license - {self.license}')
        # Проверяем согласованность полей use_license и license
        if self.use_license and not self.license:
            raise ValidationError(
                {'license': 'Если отмечено "Используется лицензия", необходимо указать ссылку на объект Лицензия.'})
        if not self.use_license and self.license:
            raise ValidationError({'license': 'Если "Используется лицензия" = Нет, поле лицензии должно быть пустым.'})

    def save(self, *args, **kwargs):
        """
        Логика сохранения:
        - Синхронизируем amount через M2M-хендлер (m2m_changed). При сохранении amount только через update_fields=['amount']
          пропускаем логику изменения лицензий (чтобы не было двойного срабатывания).
        - Обрабатываем случаи создания/изменения/смены лицензии и изменения use_license.
        - При обновлениях лицензий используем атомарные update() с F-выражениями и корректируем одновременно free.
        """
        # Если это сохранение только поля amount -> пропускаем логику корректировки лицензий
        update_fields = kwargs.get('update_fields')
        only_amount_update = update_fields == ['amount']

        # Выполним валидацию
        self.full_clean()

        # Получаем старое состояние только если это не update_fields=['amount']
        old = None
        if not only_amount_update and self.pk:
            try:
                old = Logbook.objects.select_related('license').get(pk=self.pk)
            except Logbook.DoesNotExist:
                old = None

        # Сохраняем сам объект
        super().save(*args, **kwargs)

        # Если это было только обновление amount, считаем что m2m handler уже скорректировал license.used
        if only_amount_update:
            return

        # Текущие значения
        curr_amount = int(self.amount or 0)
        curr_license = self.license
        curr_use = bool(self.use_license)

        # Старые значения
        old_amount = int(old.amount or 0) if old else 0
        old_license = old.license if old else None
        old_use = bool(old.use_license) if old else False

        # Обрабатываем варианты
        # 1) Создание новой записи: old is None
        if old is None:
            if curr_use and curr_license:
                License.objects.filter(pk=curr_license.pk).update(
                    used=F('used') + curr_amount,
                    free=F('free') - curr_amount
                )
            return

        # 2) Была лицензия раньше, но теперь не используется или лицензия снята
        if old_use and (not curr_use or curr_license is None):
            if old_license:
                License.objects.filter(pk=old_license.pk).update(
                    used=F('used') - old_amount,
                    free=F('free') + old_amount
                )
            return

        # 3) Использование лицензии продолжается и лицензия не менялась
        if old_use and curr_use and old_license and curr_license and old_license.pk == curr_license.pk:
            delta = curr_amount - old_amount
            if delta != 0:
                License.objects.filter(pk=curr_license.pk).update(
                    used=F('used') + delta,
                    free=F('free') - delta
                )
            return

        # 4) Смена лицензии: вычесть из старой и прибавить к новой
        if old_use and curr_use and old_license and curr_license and old_license.pk != curr_license.pk:
            # вычитаем из старой
            License.objects.filter(pk=old_license.pk).update(
                used=F('used') - old_amount,
                free=F('free') + old_amount
            )
            # прибавляем к новой
            License.objects.filter(pk=curr_license.pk).update(
                used=F('used') + curr_amount,
                free=F('free') - curr_amount
            )
            return

        # 5) Раньше не было лицензии/не использовалась, а теперь используется
        if (not old_use) and curr_use and curr_license:
            License.objects.filter(pk=curr_license.pk).update(
                used=F('used') + curr_amount,
                free=F('free') - curr_amount
            )
        # Если это было только обновление amount, пропускаем
        if kwargs.get('update_fields') == ['amount']:
            return

        # # Обновляем поля у абонентов, если пустые
        # if self.abonents.exists():
        #     for abonent in self.abonents.all():
        #         updated = False
        #
        #         # Обновляем net_number, только если пуст
        #         if not abonent.net_number:
        #             abonent.net_number = self.net_number
        #             updated = True
        #
        #         # Обновляем platform, только если пуст
        #         if not abonent.platform:
        #             abonent.platform = self.platform
        #             updated = True
        #
        #         # Сохраняем абонента, только если были изменения
        #         if updated:
        #             abonent.save()

    def update_amount(self):
        # Обновляем amount по количеству абонентов и сохраняем только поле amount
        new_amount = self.abonents.count()
        if new_amount != (self.amount or 0):
            self.amount = new_amount
            # Сохраняем только amount — в save() предусмотрена логика пропуска лицензий при update_fields=['amount']
            self.save(update_fields=['amount'])

    def delete(self, *args, **kwargs):
        # Перед удалением уменьшаем used и увеличиваем free в лицензии, если была привязка
        if self.license and self.use_license:
            License.objects.filter(pk=self.license.pk).update(
                used=F('used') - (self.amount or 0),
                free=F('free') + (self.amount or 0)
            )
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-log_number', '-date_of_request', 'status', '-date_of_receipt', '-number_naumen', '-number_elk']
        verbose_name = 'Выдача'
        verbose_name_plural = 'Журнал'

# M2M handler: следим за изменением связей abonents -> корректируем License.used и поле amount
@receiver(m2m_changed, sender=Logbook.abonents.through)
def logbook_abonents_changed(sender, instance, action, pk_set, **kwargs):
    # Нас интересуют только post_* события
    if action not in ('post_add', 'post_remove', 'post_clear'):
        return

    try:
        new_count = instance.abonents.count()
    except Exception:
        # если instance ещё не сохранён корректно — выходим
        return

    old_count = int(instance.amount or 0)
    delta = new_count - old_count
    if delta == 0:
        # просто синхронизируем поле amount, если оно не совпадает
        if new_count != old_count:
            instance.amount = new_count
            instance.save(update_fields=['amount'])
        return

    # Если запись использует лицензию, корректируем used/free
    if instance.use_license and instance.license:
        License.objects.filter(pk=instance.license.pk).update(
            used=F('used') + delta,
            free=F('free') - delta
        )

    # обновляем amount через save(update_fields=['amount']) — save пропустит логику работы с лицензией
    instance.amount = new_count
    instance.save(update_fields=['amount'])