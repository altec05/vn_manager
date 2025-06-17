from django.shortcuts import render, redirect


def home(request):
    context = {
        'current_version': '1.4',  # текущая версия
        'updated_at': '17.06.2025',  # последнее изменение
    }
    return render(request, 'home.html', context)