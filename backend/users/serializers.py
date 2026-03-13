from rest_framework import serializers
from .models import User, ManagerPermission

class ManagerPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerPermission
        fields = ['can_see_revenue', 'can_see_transactions', 'can_add_users', 'can_manage_sites', 'can_edit_past_dates', 'assigned_site']

class UserSerializer(serializers.ModelSerializer):
    manager_permissions = ManagerPermissionSerializer(read_only=True)
    unread_count = serializers.IntegerField(read_only=True, default=0)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone_number', 'manager_permissions', 'unread_count']
        extra_kwargs = {'password': {'write_only': True}}
