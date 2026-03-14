from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('add/', views.product_create, name='add'),
    path('<int:pk>/', views.product_detail, name='detail'),
    path('<int:pk>/edit/', views.product_update, name='edit'),
    path('<int:pk>/delete/', views.product_delete, name='delete'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/add/', views.category_create, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
