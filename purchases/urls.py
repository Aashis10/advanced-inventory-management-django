from django.urls import path

from . import views

app_name = 'purchases'

urlpatterns = [
    path('', views.purchase_list, name='list'),
    path('add/', views.purchase_create, name='add'),
    path('<int:pk>/edit/', views.purchase_update, name='edit'),
]
