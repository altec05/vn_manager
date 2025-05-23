from django.shortcuts import render, redirect


def home(request):
    context = {
        'current_version': '1.1',  # текущая версия
        'updated_at': '23.05.2025',  # последнее изменение
    }
    return render(request, 'home.html', context)