from django.shortcuts import render, redirect


def home(request):
    context = {
        'current_version': '1.8',  # текущая версия
        'updated_at': '11.12.2025',  # последнее изменение
    }
    return render(request, 'home.html', context)