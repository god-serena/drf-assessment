from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import RegexValidator

class Roles(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrator'
    DRIVER = 'DRIVER', 'Driver'
    RIDER = 'RIDER', 'Rider'

class UserManager(UserManager):
    def create_user(self, username, email, password, **kwargs):
        pass
    def create_superuser(self, username, email, password, **kwargs):
        pass
        
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length = 13,
        validators = [
            RegexValidator(
                regex = r'^\+639\d{9}$',
                message = 'Enter a value in the +639XXXXXXXXX format.'
            )
        ]
    )
    role = models.CharField(
        max_length=15,
        choices=Roles.choices
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check = models.Q(phone_number__regex = r'^\+639\d{9}$'),
                name = 'ph_phone_number_international_format_constraint',
            )
        ]
    