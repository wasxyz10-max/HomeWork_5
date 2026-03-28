from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    groups = models.ManyToManyField( 'auth.Group', related_name='custom_user_set', blank=True, verbose_name='groups',help_text='The groups this user belongs to.',)
    user_permissions = models.ManyToManyField( 'auth.Permission', related_name='custom_user_set', blank=True, verbose_name='user permissions', help_text='Specific permissions for this user.',)
    
    def __str__(self):
        return self.email

class EmailConfirmationCode(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='confirmation_code'
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at