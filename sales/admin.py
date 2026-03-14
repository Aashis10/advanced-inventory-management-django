from django.contrib import admin

from .models import Sale


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
	list_display = (
		'product',
		'buyer_name',
		'quantity',
		'total_price',
		'amount_paid',
		'balance_due',
		'profit',
		'date',
		'sold_by',
	)
	list_filter = ('date', 'sold_by', 'payment_method')
	search_fields = ('product__name', 'sold_by__username', 'buyer_name')
