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

from .models import MilkSupplyRecord, MilkSaleRecord, Expense, MilkLoss, Loan, BuyerLoan, PaymentRecord

class BuyerLoanForm(forms.ModelForm):
    class Meta:
        model = BuyerLoan
        fields = ['buyer', 'amount', 'description']
        widgets = {
            'buyer': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl border-gray-200'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-gray-200'}),
            'description': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-gray-200'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentRecord
        fields = ['payment_type', 'supplier', 'buyer', 'worker', 'amount', 'note']
        widgets = {
            'payment_type': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl border-gray-200'}),
            'supplier': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl border-gray-200'}),
            'buyer': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl border-gray-200'}),
            'worker': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl border-gray-200'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-gray-200'}),
            'note': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-gray-200'}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['site', 'category', 'amount', 'description', 'date']
        widgets = {
            'site': forms.Select(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-blue-500 focus:border-blue-500'}),
            'category': forms.Select(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-blue-500 focus:border-blue-500'}),
            'amount': forms.NumberInput(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Amount in RWF'}),
            'description': forms.Textarea(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-blue-500 focus:border-blue-500', 'rows': 2, 'placeholder': 'e.g., Fuel for transport'}),
            'date': forms.DateInput(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-blue-500 focus:border-blue-500', 'type': 'date'}),
        }

class MilkLossForm(forms.ModelForm):
    class Meta:
        model = MilkLoss
        fields = ['site', 'litres', 'reason', 'date']
        widgets = {
            'site': forms.Select(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-red-500 focus:border-red-500'}),
            'litres': forms.NumberInput(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-red-500 focus:border-red-500', 'placeholder': 'Lost Litres'}),
            'reason': forms.TextInput(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-red-500 focus:border-red-500', 'placeholder': 'e.g., Spillage during transport'}),
            'date': forms.DateInput(attrs={'class': 'block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-red-500 focus:border-red-500', 'type': 'date'}),
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
