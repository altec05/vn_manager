from django.shortcuts import render, redirect


def home(request):
    context = {
        'current_version': '1.7',  # текущая версия
        'updated_at': '28.08.2025',  # последнее изменение
    }
    return render(request, 'home.html', context)