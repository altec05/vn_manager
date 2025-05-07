from django.urls import path
from . import views

app_name = 'Queue'  # Важно для использования reverse_lazy

urlpatterns = [
    path('newrecipient/', views.NewRecipientListView.as_view(), name='newrecipient_list'),
    path('newrecipient/<int:pk>/', views.NewRecipientDetailView.as_view(), name='newrecipient_detail'),
    path('newrecipient/create/', views.NewRecipientCreateView.as_view(), name='newrecipient_create'),
    path('newrecipient/<int:pk>/update/', views.NewRecipientUpdateView.as_view(), name='newrecipient_update'),
    path('newrecipient/<int:pk>/delete/', views.NewRecipientDeleteView.as_view(), name='newrecipient_delete'),
]