import io
import xlsxwriter
from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime
from .models import Logbook
from .forms import ExportLogbookForm

def logbook_list(request):
    logbooks = Logbook.objects.exclude(log_number__isnull=True).exclude(authority__name__isnull=True).prefetch_related('abonents__owner', 'abonents__client')
    # logbooks = Logbook.objects.all()
    if request.method == 'POST':
        form = ExportLogbookForm(request.POST)
        if form.is_valid():
            selected_ids = form.cleaned_data['selected_ids']
            export_to_excel = form.cleaned_data['export_to_excel']

            if export_to_excel and selected_ids:
                # Фильтруем Logbook по выбранным ID
                logbooks_to_export = Logbook.objects.filter(pk__in=selected_ids).prefetch_related(
                    'abonents__owner', 'abonents__client'
                )

                # Создаем Excel-файл в памяти
                output = io.BytesIO()
                workbook = xlsxwriter.Workbook(output, {'in_memory': True})
                worksheet = workbook.add_worksheet('Logbook')

                # Форматы
                bold_format = workbook.add_format({'bold': True, 'border': 1, 'valign': 'center', 'align': 'center'}) #bold_format
                border_format = workbook.add_format({'border': 1, 'valign': 'vcenter', 'align': 'center'})#border_format
                center_align_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
                left_align_format = workbook.add_format({'align': 'left','valign': 'vcenter'})

                # Заголовки столбцов
                header_row = [
                    '№ П/П в Журнале', 'Дата запроса', 'Дата выдачи dst', 'Основание выдачи', '№ запроса',
                    '№ ЕЛК', 'Организация', 'Клиентов', 'ФИО', 'Имя клиента', 'Тип',
                    '№ сети', 'Примечание'
                ]
                for col_num, column_title in enumerate(header_row):
                    worksheet.write(0, col_num, column_title, bold_format)

                row_num = 1  # Начинаем со второй строки, так как первая строка - заголовки

                # Записываем данные
                for logbook in logbooks_to_export:
                    fio_list = []
                    clients_list = []
                    for abonent in logbook.abonents.all():
                        fio_list.append(abonent.owner.full_name)
                        clients_list.append(abonent.client.client_name)

                    # Определяем максимальную длину списков
                    max_len = max(len(fio_list), len(clients_list)) if (fio_list or clients_list) else 1

                    # Если списки пустые, добавляем пустые значения для избежания ошибок
                    if not fio_list:
                        fio_list = ['']
                    if not clients_list:
                        clients_list = ['']
                    # Перебираем значения и записываем строки
                    for i in range(max_len):
                        fio = fio_list[i] if i < len(fio_list) else ''
                        client = clients_list[i] if i < len(clients_list) else ''

                        # Если это первая строка для данной записи, записываем все поля
                        if i == 0:
                            row = [
                                int(logbook.log_number),
                                logbook.date_of_request.strftime('%d.%m.%y') if logbook.date_of_request else '',
                                logbook.date_of_receipt.strftime('%d.%m.%y') if logbook.date_of_receipt else '',
                                logbook.authority.name,
                                logbook.number_naumen,
                                int(logbook.number_elk),
                                logbook.ogv,
                                int(logbook.amount),
                                fio,
                                client,
                                logbook.platform.platform_name,
                                logbook.net_number.vipnet_net_number,
                                logbook.note,
                            ]
                            for col_num, cell_value in enumerate(row):
                                worksheet.write(row_num, col_num, str(cell_value), border_format)
                        # Иначе записываем только ФИО и Имя клиента
                        else:
                            worksheet.write(row_num, 8, fio, border_format)  # Колонка ФИО (индекс 8)
                            worksheet.write(row_num, 9, client, border_format)  # Колонка Имя клиента (индекс 9)
                            for col_num in range(0, 8):
                                worksheet.write(row_num, col_num, '', border_format)
                            for col_num in range(10, 13):
                                worksheet.write(row_num, col_num, '', border_format)

                        row_num += 1

                    # Автоматическая ширина столбцов
                for col_num in range(len(header_row)):
                    worksheet.set_column(col_num, col_num, 15)  # Значение можно подбирать

                workbook.close()

                # Собираем данные для имени файла
                record_count = len(logbooks_to_export)
                current_date = datetime.now().strftime('%d_%m_%y')
                filename = f"{record_count}_export_{current_date}.xlsx"

                # Подготавливаем HTTP-ответ
                output.seek(0)
                response = HttpResponse(output.read(),
                                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response

    else:
        form = ExportLogbookForm()

    return render(request, 'issuance/logbook_list.html', {'logbooks': logbooks, 'form': form})
