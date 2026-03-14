from django.urls import path

from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list, name='list'),
    path('add/', views.sale_create, name='add'),
]
