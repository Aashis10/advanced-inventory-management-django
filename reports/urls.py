from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_home, name='home'),
    path('sales/csv/', views.sales_report_csv, name='sales_csv'),
    path('purchase/csv/', views.purchase_report_csv, name='purchase_csv'),
    path('inventory/csv/', views.inventory_report_csv, name='inventory_csv'),
    path('low-stock/csv/', views.low_stock_report_csv, name='low_stock_csv'),
    path('profit/csv/', views.profit_report_csv, name='profit_csv'),
    path('sales/pdf/', views.sales_report_pdf, name='sales_pdf'),
    path('purchase/pdf/', views.purchase_report_pdf, name='purchase_pdf'),
    path('inventory/pdf/', views.inventory_report_pdf, name='inventory_pdf'),
    path('low-stock/pdf/', views.low_stock_report_pdf, name='low_stock_pdf'),
    path('profit/pdf/', views.profit_report_pdf, name='profit_pdf'),
]
