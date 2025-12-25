# licenses/models.py
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

# Если у вас Django >= 3.2 можно использовать PositiveBigIntegerField для INN,
# ниже использован PositiveIntegerField (подойдёт для INN длиной до 10 цифр).
# При необходимости замените на PositiveBigIntegerField.

class License(models.Model):
    network_number = models.PositiveIntegerField(verbose_name='№ сети', db_index=True)
    organization_name = models.CharField(max_length=255, verbose_name='Наименование организации')
    inn = models.PositiveBigIntegerField(verbose_name='ИНН')
    license_object = models.CharField(max_length=255, verbose_name='Объект лицензии')
    valid_until = models.DateField(verbose_name='Срок действия лицензии', blank=True, null=True)


    total_received = models.PositiveIntegerField(
        verbose_name='Количество поступивших лицензий',
        default=0
    )
    last_replenishment = models.DateField(
        verbose_name='Дата последнего пополнения',
        blank=True,
        null=True
    )
    used = models.PositiveIntegerField(
        verbose_name='Использовано лицензий',
        default=0
    )
    free = models.IntegerField(verbose_name='Свободно лицензий', default=0)
    note = models.TextField(verbose_name='Примечание', blank=True, null=True)

    class Meta:
        verbose_name = 'Лицензия'
        verbose_name_plural = 'Лицензии'
        unique_together = ('inn', 'organization_name', 'license_object', 'valid_until')
        ordering = ['organization_name', 'inn', 'license_object']

    def __str__(self):
        if not self.note is None and self.note.strip() != '':
            if self.valid_until:
                return f"№ {self.network_number} / {self.organization_name} (ИНН: {self.inn}) — {self.license_object}. /// Свободно: {self.free} /// До: {self.valid_until.strftime('%d.%m.%Y')} /// [{self.note}]"
            else:
                return f"№ {self.network_number} / {self.organization_name} (ИНН: {self.inn}) — {self.license_object}. /// Свободно: {self.free} /// [{self.note}]"
        else:
            if self.valid_until:
                return f"№ {self.network_number} / {self.organization_name} (ИНН: {self.inn}) — {self.license_object}. /// Свободно: {self.free} /// До: {self.valid_until.strftime('%d.%m.%Y')}"
            else:
                return f"№ {self.network_number} / {self.organization_name} (ИНН: {self.inn}) — {self.license_object}. /// Свободно: {self.free}"

    def recalc_free(self):
        # свободно = поступило - использовано (может быть < 0)
        self.free = (self.total_received or 0) - (self.used or 0)

    def clean(self):
        if self.organization_name:
            # Убираем пробелы по краям и кавычки
            self.organization_name = self.organization_name.replace('"', '').replace("'", "").strip()

    def save(self, *args, **kwargs):
        self.clean()  # вызываем очистку перед сохранением
        self.recalc_free()
        super().save(*args, **kwargs)

class Arrival(models.Model):
    date = models.DateField(verbose_name='Дата поступления')
    request_number = models.CharField(verbose_name='Номер заявки', max_length=255)
    network_number = models.PositiveIntegerField(verbose_name='№ сети')
    organization_name = models.CharField(max_length=255, verbose_name='Наименование организации')
    inn = models.PositiveBigIntegerField(verbose_name='ИНН')
    valid_until = models.DateField(verbose_name='Срок действия лицензии', blank=True, null=True)
    license_object = models.CharField(max_length=255, verbose_name='Объект лицензии')
    quantity = models.PositiveIntegerField(verbose_name='Количество по лицензии')
    uploaded = models.BooleanField(verbose_name='Статус загрузки в сеть', default=False)
    uploaded_date = models.DateField(verbose_name='Дата загрузки в сеть', blank=True, null=True)
    note = models.TextField(verbose_name='Примечание', blank=True, null=True)

    # связь с License: при удалении License связанные Arrival должны удаляться
    license = models.ForeignKey(
        License,
        on_delete=models.CASCADE,
        related_name='arrivals',
        blank=True,
        null=True,
        verbose_name='Лицензия (связь)'
    )

    class Meta:
        verbose_name = 'Поступление'
        verbose_name_plural = 'Поступления'
        ordering = ['-date', 'request_number', 'organization_name']

    def __str__(self):
        return f"{self.request_number} / {self.organization_name} / {self.license_object} / {self.quantity}"

    def clean(self):
        super().clean()  # вызвать валидацию родителя
        if self.organization_name:
            self.organization_name = self.organization_name.replace('"', '').replace("'", "").strip()

        # Валидация: uploaded <-> uploaded_date
        if self.uploaded:
            if not self.uploaded_date:
                raise ValidationError({'uploaded_date': 'Если выбран статус загрузки в сеть (Да), необходимо указать дату загрузки.'})
        else:
            # если uploaded == False, uploaded_date должен быть пустым
            if self.uploaded_date:
                raise ValidationError({'uploaded_date': 'Если статус загрузки в сеть (Нет), то поле "Дата загрузки" должно быть пустым.'})

    @transaction.atomic
    def save(self, *args, **kwargs):
        # воспроизводим логику: поиск/создание License по INN, org, license_object.
        # при создании/обновлении корректируем License.total_received и last_replenishment.
        self.full_clean()  # обязательно проверить clean()

        is_create = self.pk is None

        # Найдём соответствующую лицензию (по ключу)
        license_obj = License.objects.filter(
            inn=self.inn,
            organization_name=self.organization_name,
            license_object=self.license_object,
            valid_until=self.valid_until,
        ).first()

        if license_obj is None:
            # Создаем новую лицензию с нулевыми значениями сумм до применения данного поступления.
            license_obj = License.objects.create(
                network_number=self.network_number,
                organization_name=self.organization_name,
                inn=self.inn,
                license_object=self.license_object,
                valid_until=self.valid_until,
                total_received=0,
                used=0,
            )

        # Обрабатываем обновление: если редактирование, нужно учесть старые значения и, возможно, старую лицензию
        old = None
        if not is_create:
            try:
                old = Arrival.objects.get(pk=self.pk)
            except Arrival.DoesNotExist:
                old = None

        # Если старый объект существует и привязан к другой лицензии/изменилось количество,
        # сначала скорректируем старую лицензию (как будто удаляем старое поступление)
        if old:
            old_license = old.license
            if old_license:
                # вычитаем старое количество
                old_license.total_received = max(0, (old_license.total_received or 0) - (old.quantity or 0))
                # пересчитать last_replenishment: берём последний arrival по этой лицензии (исключая текущий old)
                last = Arrival.objects.filter(license=old_license).exclude(pk=old.pk).order_by('-date').first()
                if last:
                    old_license.last_replenishment = last.date
                else:
                    old_license.last_replenishment = None
                old_license.save()

        # Теперь назначаем текущему Arrival ссылку на найденную/созданную лицензию
        self.license = license_obj

        # И увеличиваем total_received у текущей лицензии на delta
        if old and old.license and old.license.pk == license_obj.pk:
            # редактировали в той же лицензии: добавляем дельту
            delta = (self.quantity or 0) - (old.quantity or 0)
        else:
            # либо новый приход, либо пришло в другую лицензию: просто добавляем текущее количество
            delta = (self.quantity or 0)

        license_obj.total_received = (license_obj.total_received or 0) + delta
        # Обновим дату последнего пополнения на дату этого поступления
        license_obj.last_replenishment = self.date
        license_obj.save()

        # сохраняем сам arrival
        super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        # при удалении нужно уменьшить total_received и пересчитать дату последнего пополнения
        lic = self.license
        qty = self.quantity or 0
        super().delete(*args, **kwargs)
        if lic:
            lic.total_received = max(0, (lic.total_received or 0) - qty)
            # найдём последнее поступление для этой лицензии
            last = Arrival.objects.filter(license=lic).order_by('-date').first()
            if last:
                lic.last_replenishment = last.date
            else:
                lic.last_replenishment = None
            lic.save()
