from rest_framework import serializers
from .models import User, ManagerPermission

class ManagerPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerPermission
        fields = ['can_see_revenue', 'can_see_transactions', 'can_add_users', 'can_manage_sites']

class UserSerializer(serializers.ModelSerializer):
    manager_permissions = ManagerPermissionSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone_number', 'manager_permissions']
        extra_kwargs = {'password': {'write_only': True}}
