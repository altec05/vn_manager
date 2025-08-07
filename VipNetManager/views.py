from django.shortcuts import render, redirect


def home(request):
    context = {
        'current_version': '1.6.1',  # текущая версия
        'updated_at': '07.08.2025',  # последнее изменение
    }
    return render(request, 'home.html', context)