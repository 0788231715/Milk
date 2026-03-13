from django.contrib import admin
from django import forms
from django.utils.text import slugify
from .models import Site, Supplier, Buyer, Worker, Announcement, JoinRequest
from users.models import User

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')

class SupplierAdminForm(forms.ModelForm):
    username = forms.CharField(required=False, help_text="Explicitly set username for login. If empty, it will be generated from name.")
    password = forms.CharField(widget=forms.PasswordInput(), required=False, help_text="Set password for the new user account.")
    
    class Meta:
        model = Supplier
        fields = '__all__'

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    form = SupplierAdminForm
    list_display = ('name', 'site', 'contact', 'current_balance')
    list_filter = ('site',)
    search_fields = ('name', 'contact')

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            username = form.cleaned_data.get('username')
            if not username:
                username = slugify(obj.name).replace('-', '_')
            
            # Ensure unique username
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
                
            password = form.cleaned_data.get('password') or 'password123'
            user = User.objects.create_user(username=username, password=password, role=User.SUPPLIER)
            user.is_staff = True
            user.save()
            obj.user = user
        super().save_model(request, obj, form, change)

class BuyerAdminForm(forms.ModelForm):
    username = forms.CharField(required=False, help_text="Explicitly set username for login. If empty, it will be generated from name.")
    password = forms.CharField(widget=forms.PasswordInput(), required=False, help_text="Set password for the new user account.")
    
    class Meta:
        model = Buyer
        fields = '__all__'

@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    form = BuyerAdminForm
    list_display = ('name', 'contact', 'current_balance')
    search_fields = ('name', 'contact')

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            username = form.cleaned_data.get('username')
            if not username:
                username = slugify(obj.name).replace('-', '_')

            # Ensure unique username
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            password = form.cleaned_data.get('password') or 'password123'
            user = User.objects.create_user(username=username, password=password, role=User.BUYER)
            user.is_staff = True
            user.save()
            obj.user = user
        super().save_model(request, obj, form, change)

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'base_pay')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_active')

@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'request_type', 'status', 'created_at', 'password')
    list_filter = ('request_type', 'status')
    search_fields = ('name', 'phone')
    fields = ('name', 'phone', 'email', 'password', 'request_type', 'message', 'status', 'created_at')
    readonly_fields = ('created_at',)

