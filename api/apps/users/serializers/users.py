from rest_framework import serializers
from django.contrib.auth import get_user_model

class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        user_model = get_user_model()
        
        model = user_model
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'phone_number'
        ]