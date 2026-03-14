from django import forms

from .models import Purchase


class PurchaseForm(forms.ModelForm):
    purchase_date = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
    )

    class Meta:
        model = Purchase
        fields = [
            'supplier_name',
            'product',
            'quantity',
            'purchase_price',
            'payment_method',
            'amount_paid',
            'purchase_date',
        ]
        widgets = {
            'supplier_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier name'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0.01}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
        }
