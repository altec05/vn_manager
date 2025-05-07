from django.urls import path
from . import views

app_name = 'Issuance'

urlpatterns = [
    path('logbook/', views.logbook_list, name='logbook_list'),
]
