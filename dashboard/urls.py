from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('analytics/', views.analytics_page, name='analytics'),
    path('search/', views.global_search, name='search'),
    path('settings/', views.settings_page, name='settings'),
]
