from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Q
from typing import Dict

# Замените на ваши приложения
from Licenses.models import License, Arrival
from Owners.models import NewAbonent

# Просмотр изменений (сухой прогон)
# python manage.py cleanup_organization_ogv --dry-run

# Запуск
# python manage.py cleanup_organization_ogv

def cleanup_organization_ogv(dry_run=False) -> Dict[str, int]:
    """
    Очищает поля:
      - License.organization_name
      - Arrival.organization_name
      - NewAbonent.ogv
    от:
      - кавычек: ", ', «, », “, ”, ‘, ’
      - пробелов в начале и конце строки.
    """
    stats = {"License": 0, "Arrival": 0, "NewAbonent": 0, "total": 0}

    # Все виды кавычек и лишних символов
    QUOTES = ['"', "'", '«', '»', '“', '”', '‘', '’']

    def clean_value(value: str) -> str:
        if not value:
            return value
        cleaned = value.strip()
        for quote in QUOTES:
            cleaned = cleaned.replace(quote, "")
        cleaned = cleaned.strip()  # ещё раз, на случай, если после удаления кавычек остались пробелы
        return cleaned

    def clean_and_update(qs, field_name: str):
        count = 0
        if dry_run:
            # Только подсчёт
            for obj in qs.iterator():
                value = getattr(obj, field_name)
                cleaned = clean_value(value)
                if value != cleaned:
                    count += 1
        else:
            # Обновление
            updated = 0
            for obj in qs.iterator():
                value = getattr(obj, field_name)
                cleaned = clean_value(value)
                if value != cleaned:
                    setattr(obj, field_name, cleaned)
                    obj.save(update_fields=[field_name])
                    updated += 1
            count = updated
        return count

    # === 1. License.organization_name ===
    license_qs = License.objects.exclude(
        Q(organization_name__isnull=True) | Q(organization_name="")
    )
    stats["License"] = clean_and_update(license_qs, "organization_name")

    # === 2. Arrival.organization_name ===
    arrival_qs = Arrival.objects.exclude(
        Q(organization_name__isnull=True) | Q(organization_name="")
    )
    stats["Arrival"] = clean_and_update(arrival_qs, "organization_name")

    # === 3. NewAbonent.ogv ===
    abonent_qs = NewAbonent.objects.exclude(Q(ogv__isnull=True) | Q(ogv=""))
    stats["NewAbonent"] = clean_and_update(abonent_qs, "ogv")

    stats["total"] = stats["License"] + stats["Arrival"] + stats["NewAbonent"]
    return stats


class Command(BaseCommand):
    help = "Очищает organization_name и ogv: удаляет кавычки (все виды) и пробелы. Работает с SQLite и PostgreSQL."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Показать, что будет изменено, без сохранения.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Определяем СУБД
        db_engine = connection.settings_dict["ENGINE"]
        if "sqlite" in db_engine:
            db_type = "SQLite"
        elif "postgresql" in db_engine:
            db_type = "PostgreSQL"
        else:
            db_type = "Unknown DB"

        self.stdout.write(f"🔧 Используется СУБД: {db_type}")

        if dry_run:
            self.stdout.write(self.style.WARNING("📌 РЕЖИМ СУХОГО ПРОГОНА: изменения НЕ будут сохранены."))
        else:
            self.stdout.write(self.style.SUCCESS("🚀 Режим: будут внесены изменения в базу данных."))

        # Выполняем очистку
        stats = cleanup_organization_ogv(dry_run=dry_run)

        # Вывод
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.NOTICE("РЕЗУЛЬТАТЫ:"))
        self.stdout.write(f"  License (organization_name): {stats['License']}")
        self.stdout.write(f"  Arrival (organization_name): {stats['Arrival']}")
        self.stdout.write(f"  NewAbonent (ogv): {stats['NewAbonent']}")
        self.stdout.write(f"  ВСЕГО: {stats['total']}")
        self.stdout.write("=" * 50)

        if dry_run:
            self.stdout.write(
                self.style.WARNING("✅ Сухой прогон завершён. База данных не изменена.")
            )
        else:
            if stats["total"] == 0:
                self.stdout.write(
                    self.style.SUCCESS("✅ Все поля уже очищены.")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS("✅ Очистка завершена! Изменения сохранены.")
                )