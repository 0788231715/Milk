from rest_framework import serializers
from .models import TrainingResource, SystemUpdate, MilkStandard

class TrainingResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingResource
        fields = '__all__'

class SystemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemUpdate
        fields = '__all__'

class MilkStandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilkStandard
        fields = '__all__'
