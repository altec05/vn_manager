from django.shortcuts import render, redirect


def home(request):
    context = {
        'current_version': '1.2',  # текущая версия
        'updated_at': '16.06.2025',  # последнее изменение
    }
    return render(request, 'home.html', context)