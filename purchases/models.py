from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from products.models import ActivityLog


class Purchase(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('online', 'Online'),
    )

    supplier_name = models.CharField(max_length=160)
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='purchases')
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='bank')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    purchase_date = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='purchases')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-purchase_date', '-id']

    def __str__(self):
        return f'Purchase #{self.pk or "new"} - {self.product.name}'

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'Quantity must be greater than zero.'})
        if self.purchase_price <= 0:
            raise ValidationError({'purchase_price': 'Purchase price must be greater than zero.'})
        if self.amount_paid < 0:
            raise ValidationError({'amount_paid': 'Amount paid cannot be negative.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        self.total_price = Decimal(self.quantity) * self.purchase_price
        self.balance_due = max(Decimal('0.00'), self.total_price - self.amount_paid)

        if not self.pk:
            self.product.quantity += self.quantity
            self.product.save(update_fields=['quantity'])
        else:
            previous = Purchase.objects.get(pk=self.pk)
            if previous.product_id == self.product_id:
                self.product.quantity += self.quantity - previous.quantity
                self.product.save(update_fields=['quantity'])
            else:
                old_product = previous.product
                old_product.quantity -= previous.quantity
                old_product.save(update_fields=['quantity'])
                self.product.quantity += self.quantity
                self.product.save(update_fields=['quantity'])

        super().save(*args, **kwargs)

        ActivityLog.record(
            action='stock_updated',
            message=f'Purchase recorded: {self.quantity} x {self.product.name} from {self.supplier_name}',
            related_product=self.product,
            user=self.created_by,
        )
