from django.contrib import admin

from .models import Purchase


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'supplier_name',
        'product',
        'quantity',
        'purchase_price',
        'total_price',
        'amount_paid',
        'balance_due',
        'payment_method',
        'purchase_date',
        'created_by',
    )
    list_filter = ('payment_method', 'purchase_date')
    search_fields = ('supplier_name', 'product__name', 'created_by__username')
