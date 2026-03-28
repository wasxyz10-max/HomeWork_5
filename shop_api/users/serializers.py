from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import random
from django.core.mail import send_mail
from django.conf import settings
from .models import User, EmailConfirmationCode

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password')
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            is_active=False
        )
        
        confirmation_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        expires_at = timezone.now() + timedelta(minutes=15)
        
        EmailConfirmationCode.objects.update_or_create(
            user=user,
            defaults={
                'code': confirmation_code,
                'expires_at': expires_at
            }
        )
        
        send_mail(
            subject='Подтверждение регистрации',
            message=f'Ваш код подтверждения: {confirmation_code}\nКод действителен 15 минут.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        return user
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['message'] = 'Регистрация успешна. Код подтверждения отправлен на email.'
        return data

class UserConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    
    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден")
        
        if user.is_active:
            raise serializers.ValidationError("Пользователь уже подтвержден")
        
        try:
            confirmation = EmailConfirmationCode.objects.get(user=user)
        except EmailConfirmationCode.DoesNotExist:
            raise serializers.ValidationError("Код подтверждения не найден")
        
        if confirmation.code != data['code']:
            raise serializers.ValidationError("Неверный код подтверждения")
        
        if confirmation.is_expired():
            raise serializers.ValidationError("Срок действия кода истек")
        
        data['user'] = user
        data['confirmation'] = confirmation
        return data
    
    def save(self):
        user = self.validated_data['user']
        confirmation = self.validated_data['confirmation']
        
        user.is_active = True
        user.save()
        
        confirmation.delete()
        
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        
        if not user:
            raise serializers.ValidationError("Неверный email или пароль")
        
        if not user.is_active:
            raise serializers.ValidationError("Аккаунт не подтвержден. Подтвердите email.")
        
        data['user'] = user
        return data