from django.contrib import admin

from .models import ActivityLog, Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'icon')
	search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('name', 'brand', 'category', 'price', 'quantity', 'reorder_level')
	list_filter = ('category',)
	search_fields = ('name', 'brand')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
	list_display = ('action', 'message', 'related_product', 'user', 'created_at')
	list_filter = ('action', 'created_at')
	search_fields = ('message', 'related_product__name', 'user__username')

# Register your models here.
