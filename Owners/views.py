# Owners/views.py
from django.http import JsonResponse
from django.urls import reverse

from .forms import ViPNetNetNumberForm, PlatformForm, NewAbonentForm

import openpyxl
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import Owner, ClientName, NewAbonent, ViPNetNetNumber

def create_vipnetnetnumber(request):
    if request.method == 'POST':
        form = ViPNetNetNumberForm(request.POST)
        if form.is_valid():
            vipnet_net_number = form.save()
            return JsonResponse({'id': vipnet_net_number.id, 'text': str(vipnet_net_number)})
        else:
            return JsonResponse({'errors': form.errors}, status=400) # Bad Request
    else:
        form = ViPNetNetNumberForm()
    return render(request, 'Owners/vipnetnetnumber_modal_form.html', {'form': form})


def create_platform(request):
    if request.method == 'POST':
        form = PlatformForm(request.POST)
        if form.is_valid():
            platform = form.save()
            return JsonResponse({'id': platform.id, 'text': str(platform)})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = PlatformForm()
    return render(request, 'Owners/platform_modal_form.html', {'form': form})

def create_newabonent(request):
    if request.method == 'POST':
        form = NewAbonentForm(request.POST)
        if form.is_valid():
            owner = form.cleaned_data['owner']
            client = form.cleaned_data['client']
            new_abonent = NewAbonent.objects.create(owner=owner, client=client)

            return JsonResponse({'id': new_abonent.id, 'text': str(new_abonent)})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = NewAbonentForm()
    return render(request, 'Owners/newabonent_modal_form.html', {'form': form})


def import_abonents_view(request):
    if request.method == 'POST':
        file = request.FILES.get('excel_file')
        if not file:
            messages.error(request, "Файл не был загружен.")
            return redirect('Owners:import_abonents')

        if not file.name.endswith('.xlsx'):
            messages.error(request, "Поддерживаются только файлы формата .xlsx.")
            return redirect('Owners:import_abonents')

        try:
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            imported_data = []
            errors = []
            # line_number будет реальным номером строки из Excel (начиная со 2 для данных)

            # Получаем ID объекта ViPNetNetNumber с vipnet_net_number = '12598'
            try:
                default_net_number_id = ViPNetNetNumber.objects.get(vipnet_net_number='12598').pk
            except ViPNetNetNumber.DoesNotExist:
                messages.error(request, "Не найден объект ViPNetNetNumber с номером '12598'. Пожалуйста, создайте его.")
                return redirect('Owners:import_abonents')

            # Пропускаем заголовок, начинаем со второй строки
            # header = [cell.value for cell in sheet[1]] # Опционально, чтобы удостовериться в заголовках

            for row_index, row in enumerate(sheet.iter_rows(min_row=2, values_only=True),
                                            start=2):  # start=2 для реальных номеров строк Excel
                line_number = row_index  # Устанавливаем номер строки для ошибок

                row_values = list(row)
                while len(row_values) < 8:  # У нас 8 ожидаемых колонок
                    row_values.append(None)

                organization, identifier, client_name, serial_number, imei, iccid, owner_name, note = row_values

                # Очистка пробелов в конце строк и приведение к строке, если None
                organization = str(organization or '').strip()
                identifier = str(identifier or '').strip()
                client_name = str(client_name or '').strip()
                serial_number = str(serial_number or '').strip()
                imei = str(imei or '').strip()
                iccid = str(iccid or '').strip()
                owner_name = str(owner_name or '').strip()
                note = str(note or '').strip()

                # Если после стриппинга поле пустое, устанавливаем его в пустую строку
                # Это важно, так как CharField/TextField с blank=True ожидает пустую строку, а не None
                organization = organization if organization else ''
                identifier = identifier if identifier else ''
                client_name = client_name if client_name else ''
                serial_number = serial_number if serial_number else ''
                imei = imei if imei else ''
                iccid = iccid if iccid else ''
                owner_name = owner_name if owner_name else ''
                note = note if note else ''

                row_data = {
                    'original_line': line_number,
                    'organization': organization,
                    'identifier': identifier,
                    'client_name': client_name,
                    'serial_number': serial_number,
                    'imei': imei,
                    'iccid': iccid,
                    'owner_name': owner_name,
                    'note': note,
                    'net_number_id': default_net_number_id,  # <-- Храним ID
                }

                current_row_errors = []

                # Проверка и создание/получение Owner
                if owner_name:
                    try:
                        owner = Owner.objects.get_or_create(full_name=owner_name)[0]
                        row_data['owner_id'] = owner.pk  # Храним только ID
                    except Exception as e:
                        current_row_errors.append(f"Ошибка при создании/поиске владельца '{owner_name}': {e}")
                else:
                    current_row_errors.append('Поле "ФИО" (owner) не может быть пустым.')

                # Проверка и создание/получение ClientName
                if client_name:
                    try:
                        client = ClientName.objects.get_or_create(client_name=client_name)[0]
                        row_data['client_id'] = client.pk  # Храним только ID
                    except Exception as e:
                        current_row_errors.append(f"Ошибка при создании/поиске клиента '{client_name}': {e}")
                else:
                    current_row_errors.append('Поле "Клиент" (VN) не может быть пустым.')

                if current_row_errors:
                    errors.append({'line': line_number, 'message': '; '.join(current_row_errors)})
                else:
                    imported_data.append(row_data)

            request.session['imported_data'] = imported_data
            request.session['import_errors'] = errors

            admin_changelist_url = reverse('admin:Owners_newabonent_changelist')
            return render(request, 'Owners/import_abonents_result.html', {
                'total_rows': len(imported_data) + len(errors),
                'successful_rows': len(imported_data),
                'error_rows': len(errors),
                'errors': errors,
                'has_errors': bool(errors),
                'pre_confirm': True,
                'admin_changelist_url': admin_changelist_url
            })

        except Exception as e:
            messages.error(request, f"Ошибка при обработке файла: {e}")
            return redirect('Owners:import_abonents')

    return render(request, 'Owners/import_abonents.html')


def import_abonents_confirm_view(request):
    if request.method == 'POST':
        imported_data = request.session.get('imported_data', [])
        import_errors_prev = request.session.get('import_errors', [])

        if not imported_data and not import_errors_prev:
            messages.error(request, "Нет данных для импорта. Пожалуйста, загрузите файл заново.")
            return redirect('Owners:import_abonents')

        successful_count = 0
        error_count = 0
        error_list = []

        # Заранее получаем объект ViPNetNetNumber, чтобы не делать это в цикле
        try:
            default_net_number = ViPNetNetNumber.objects.get(vipnet_net_number='12598')
        except ViPNetNetNumber.DoesNotExist:
            messages.error(request, "Не найден объект ViPNetNetNumber с номером '12598'. Импорт невозможен.")
            return redirect('Owners:import_abonents')

        with transaction.atomic():
            for data in imported_data:
                try:
                    owner_obj = Owner.objects.get(pk=data['owner_id'])
                    client_obj = ClientName.objects.get(pk=data['client_id'])
                    # Здесь мы используем default_net_number, полученный выше
                    net_number_obj = default_net_number  # Присваиваем объект по умолчанию

                    NewAbonent.objects.create(
                        owner=owner_obj,
                        client=client_obj,
                        net_number=net_number_obj,  # <-- Добавлено поле net_number
                        identifier=data.get('identifier', ''),
                        ogv=data.get('organization', ''),
                        serial_number=data.get('serial_number', ''),
                        imei=data.get('imei', ''),
                        iccid=data.get('iccid', ''),
                        note=data.get('note', '')
                    )
                    successful_count += 1
                except Exception as e:
                    error_count += 1
                    error_list.append(
                        {'line': data.get('original_line', 'N/A'), 'message': f"Ошибка при создании абонента: {e}"})

        final_errors = import_errors_prev + error_list

        messages.success(request, f"Импорт завершен. Успешно добавлено: {successful_count} строк.")
        if error_count > 0:
            messages.warning(request, f"Ошибок при добавлении: {error_count}.")

        request.session.pop('imported_data', None)
        request.session.pop('import_errors', None)

        admin_changelist_url = reverse('admin:Owners_newabonent_changelist')
        return render(request, 'Owners/import_abonents_result.html', {
            'total_rows': successful_count + error_count + len(import_errors_prev),
            'successful_rows': successful_count,
            'error_rows': error_count + len(import_errors_prev),
            'errors': final_errors,
            'has_errors': bool(final_errors),
            'pre_confirm': False,
            'admin_changelist_url': admin_changelist_url
        })
    else:
        imported_data = request.session.get('imported_data', [])
        import_errors = request.session.get('import_errors', [])

        if not imported_data and not import_errors:
            messages.warning(request, "Нет данных для подтверждения. Пожалуйста, загрузите файл для импорта.")
            return redirect('Owners:import_abonents')

        admin_changelist_url = reverse('admin:Owners_newabonent_changelist')
        return render(request, 'Owners/import_abonents_result.html', {
            'total_rows': len(imported_data) + len(import_errors),
            'successful_rows': len(imported_data),
            'error_rows': len(import_errors),
            'errors': import_errors,
            'has_errors': bool(import_errors),
            'pre_confirm': True,
            'admin_changelist_url': admin_changelist_url  # <-- ДОБАВЛЕНО
        })
