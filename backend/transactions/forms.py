from django import forms
from .models import MilkSupplyRecord, MilkSaleRecord
from business.models import Supplier, Buyer, Site

class MilkSupplyForm(forms.ModelForm):
    class Meta:
        model = MilkSupplyRecord
        fields = ['supplier', 'site', 'litres', 'price_per_litre', 'quality_rating']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-blue-500 focus:border-blue-500 transition-all'}),
            'site': forms.Select(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-blue-500 focus:border-blue-500 transition-all'}),
            'litres': forms.NumberInput(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-blue-500 focus:border-blue-500 transition-all', 'placeholder': 'Amount in Litres'}),
            'price_per_litre': forms.NumberInput(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-blue-500 focus:border-blue-500 transition-all', 'placeholder': 'Price per Litre'}),
            'quality_rating': forms.Select(choices=[(i, f"{i}/10") for i in range(1, 11)], attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-blue-500 focus:border-blue-500 transition-all'}),
        }

class MilkSaleForm(forms.ModelForm):
    class Meta:
        model = MilkSaleRecord
        fields = ['buyer', 'site_source', 'litres', 'price_per_litre']
        widgets = {
            'buyer': forms.Select(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-indigo-500 focus:border-indigo-500 transition-all'}),
            'site_source': forms.Select(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-indigo-500 focus:border-indigo-500 transition-all'}),
            'litres': forms.NumberInput(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-indigo-500 focus:border-indigo-500 transition-all', 'placeholder': 'Amount in Litres'}),
            'price_per_litre': forms.NumberInput(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-indigo-500 focus:border-indigo-500 transition-all', 'placeholder': 'Selling Price per Litre'}),
        }
