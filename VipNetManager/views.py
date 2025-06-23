from django.shortcuts import render, redirect


def home(request):
    context = {
        'current_version': '1.5',  # текущая версия
        'updated_at': '23.06.2025',  # последнее изменение
    }
    return render(request, 'home.html', context)