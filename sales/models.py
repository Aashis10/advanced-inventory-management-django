from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from products.models import ActivityLog


class Sale(models.Model):
	PAYMENT_METHOD_CHOICES = (
		('cash', 'Cash'),
		('bank', 'Bank'),
		('online', 'Online'),
	)

	product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='sales')
	buyer_name = models.CharField(max_length=140)
	payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
	quantity = models.PositiveIntegerField()
	total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
	amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	balance_due = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
	profit = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
	date = models.DateTimeField(auto_now_add=True)
	sold_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sales')

	class Meta:
		ordering = ['-date']

	def __str__(self):
		return f'Sale #{self.pk or "new"} - {self.product.name}'

	def clean(self):
		if self.quantity <= 0:
			raise ValidationError({'quantity': 'Quantity must be greater than zero.'})
		if self.amount_paid < 0:
			raise ValidationError({'amount_paid': 'Amount paid cannot be negative.'})

		if not self.pk and self.product and self.quantity > self.product.quantity:
			raise ValidationError({'quantity': 'Not enough stock available for this sale.'})

		if self.pk and self.product_id:
			previous = Sale.objects.get(pk=self.pk)
			if previous.product_id == self.product_id:
				available = self.product.quantity + previous.quantity
			else:
				available = self.product.quantity
			if self.quantity > available:
				raise ValidationError({'quantity': 'Not enough stock available for this sale update.'})

	def save(self, *args, **kwargs):
		self.full_clean()
		self.total_price = Decimal(self.quantity) * self.product.price
		self.balance_due = max(Decimal('0.00'), self.total_price - self.amount_paid)

		unit_profit = self.product.price * Decimal('0.18')
		self.profit = unit_profit * Decimal(self.quantity)

		if not self.pk:
			self.product.quantity -= self.quantity
			self.product.save(update_fields=['quantity'])
		else:
			previous = Sale.objects.get(pk=self.pk)
			if previous.product_id == self.product_id:
				stock_delta = previous.quantity - self.quantity
				self.product.quantity += stock_delta
				self.product.save(update_fields=['quantity'])
			else:
				old_product = previous.product
				old_product.quantity += previous.quantity
				old_product.save(update_fields=['quantity'])
				self.product.quantity -= self.quantity
				self.product.save(update_fields=['quantity'])

		super().save(*args, **kwargs)

		if self.quantity > 0:
			ActivityLog.record(
				action='sale_recorded',
				message=f'Sale recorded: {self.quantity} x {self.product.name} for {self.buyer_name}',
				related_product=self.product,
				user=self.sold_by,
			)
