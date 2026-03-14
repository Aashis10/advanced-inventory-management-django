from django import forms

from .models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon', 'image', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Laptops'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fa-solid fa-laptop'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'brand',
            'supplier_name',
            'price',
            'quantity',
            'reorder_level',
            'image',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MacBook Air M2'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apple'}),
            'supplier_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Aashish Electronics Wholesale'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
