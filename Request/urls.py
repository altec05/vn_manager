from django.urls import path
from . import views

app_name = 'Request'

urlpatterns = [
    path('', views.NewReqListView.as_view(), name='newreq_list'),
    path('new/', views.NewReqCreateView.as_view(), name='newreq_create'),
    path('<int:pk>/', views.NewReqDetailView.as_view(), name='newreq_detail'),
    path('<int:pk>/edit/', views.NewReqUpdateView.as_view(), name='newreq_update'),
    path('<int:pk>/delete/', views.NewReqDeleteView.as_view(), name='newreq_delete'),

    # URLs для создания объектов из модальных окон
    path('create_new_abonent/', views.create_new_abonent, name='create_new_abonent'),
    path('create_platform/', views.create_platform, name='create_platform'),
    path('create_vipnetnetnumber/', views.create_vipnetnetnumber, name='create_vipnetnetnumber'),
]

# urlpatterns = [
#     path('newreq/list/', views.NewReqListView.as_view(), name='newreq_list'),
#     path('newreq/<int:pk>/detail/', views.NewReqDetailView.as_view(), name='newreq_detail'),
#     path('newreq/create/', views.NewReqCreateView.as_view(), name='newreq_create'),
#     path('newreq/<int:pk>/update/', views.NewReqUpdateView.as_view(), name='newreq_update'),
#     path('newreq/<int:pk>/delete/', views.NewReqDeleteView.as_view(), name='newreq_delete'),
# ]