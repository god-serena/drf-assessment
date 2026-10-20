from django.db.models import (CharField, BooleanField, TextChoices, EmailField,
                              CheckConstraint, DateTimeField, Q )
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator

class Roles(TextChoices):
    ADMIN = 'admin', 'Administrator'
    DRIVER = 'driver', 'Driver'
    RIDER = 'rider', 'Rider'

class UserManager(BaseUserManager):
    def create_user(self, email, password = None, **kwargs):
        if not email:
            raise ValueError('The email must be set')
        email = self.normalize_email(email)
        user = self.model(email = email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **kwargs):
        kwargs['is_staff'] = True
        kwargs['is_superuser'] = True
        kwargs['role'] = Roles.ADMIN.value
        
        return self.create_user(email, password, **kwargs)
        
class User(AbstractBaseUser, PermissionsMixin):
    email = EmailField(unique=True)
    first_name = CharField(max_length=150, blank=True)
    last_name = CharField(max_length=150, blank=True)
    phone_number = CharField(
        unique=True,
        max_length = 13,
        validators = [
            RegexValidator(
                regex = r'^\+639\d{9}$',
                message = 'Enter a value in the +639XXXXXXXXX format.'
            )
        ]
        )
    date_joined = DateTimeField(auto_now_add = True)
    is_staff = BooleanField(
        default = False,
        db_default=False
        )
    is_active = BooleanField(
        default = True,
        db_default = True
        )
    role = CharField(
        max_length=15,
        choices=Roles.choices
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']
    
    objects = UserManager()
    
    class Meta:
        constraints = [
            CheckConstraint(
                check = Q(phone_number__regex = r'^\+639\d{9}$'),
                name = 'ph_phone_number_international_format_constraint',
            ),
            CheckConstraint(
                check = Q(role__in = Roles.values),
                name = 'role_constraint'
            )
        ]
    