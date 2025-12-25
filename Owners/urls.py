# Owners/urls.py
from django.urls import path
from . import views

app_name = 'Owners'

urlpatterns = [
    path('create_vipnetnetnumber/', views.create_vipnetnetnumber, name='create_vipnetnetnumber'),
    path('create_platform/', views.create_platform, name='create_platform'),
    path('create_newabonent/', views.create_newabonent, name='create_newabonent'),
    path('import_abonents/', views.import_abonents_view, name='import_abonents'),
    path('import_abonents_confirm/', views.import_abonents_confirm_view, name='import_abonents_confirm'),
]
