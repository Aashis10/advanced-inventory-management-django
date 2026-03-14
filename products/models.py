from django.conf import settings
from django.db import models


class Category(models.Model):
	name = models.CharField(max_length=120, unique=True)
	icon = models.CharField(max_length=80, default='fa-solid fa-microchip')
	image = models.ImageField(upload_to='categories/', blank=True, null=True)
	description = models.TextField(blank=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class Product(models.Model):
	name = models.CharField(max_length=180)
	brand = models.CharField(max_length=120)
	supplier_name = models.CharField(max_length=160, blank=True)
	category = models.ForeignKey('products.Category', on_delete=models.PROTECT, related_name='products')
	price = models.DecimalField(max_digits=10, decimal_places=2)
	quantity = models.PositiveIntegerField(default=0)
	reorder_level = models.PositiveIntegerField(default=5)
	image = models.ImageField(upload_to='products/', blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'{self.name} ({self.brand})'

	@property
	def is_out_of_stock(self):
		return self.quantity == 0

	@property
	def is_low_stock(self):
		return 0 < self.quantity <= self.reorder_level

	@property
	def stock_status(self):
		if self.is_out_of_stock:
			return 'out'
		if self.quantity <= self.reorder_level:
			return 'low'
		return 'in'

	@property
	def inventory_value(self):
		return self.price * self.quantity


class ActivityLog(models.Model):
	ACTION_CHOICES = (
		('product_added', 'Product Added'),
		('sale_recorded', 'Sale Recorded'),
		('stock_updated', 'Stock Updated'),
	)

	action = models.CharField(max_length=40, choices=ACTION_CHOICES)
	message = models.CharField(max_length=255)
	related_product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return self.message

	@classmethod
	def record(cls, action, message, related_product=None, user=None):
		return cls.objects.create(action=action, message=message, related_product=related_product, user=user)

# Create your models here.
