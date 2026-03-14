from django import forms

from .models import Sale


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['buyer_name', 'product', 'quantity', 'payment_method', 'amount_paid']
        widgets = {
            'buyer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buyer full name'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
        }
