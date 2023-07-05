from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager,DriverManager,AdminManager
import datetime
from random import randint
from django.utils import timezone


class ModelWithTimestamps(models.Model):
    """Абстрактная модель с таймстемпами"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='updated_at')
    class Meta:
        abstract = True

# Create your models here.
class User(AbstractUser,ModelWithTimestamps):
    """Пользователь"""
    class UserRole(models.TextChoices):
        CLIENT = 'client'
        DRIVER = 'driver'
        ADMIN = 'admin'

    role = models.CharField(max_length=20, choices=UserRole.choices)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=40, null=True)
    confirmed_at = models.DateTimeField(null=True)
    blocked_at = models.DateTimeField(null=True)
    reason = models.TextField(null=True)
    is_block = models.BooleanField(default=False)
    last_login = None
    admin_name = None

    objects = UserManager()

    REQUIRED_FIELDS = ['phone']

    @property
    def confirm(self):
        self.confirmed_at = timezone.now()
        self.save()

    def is_admin(self):
        """Является ли админом"""

        admin_role = str(self.UserRole.ADMIN)
        return self.role == admin_role

    def is_driver(self):
        """Является ли покупателем"""
        driver_role = str(self.UserRole.DRIVER)
        return self.role == driver_role

    def is_customer(self):
        """Является ли продавцом"""

        client_role = str(self.UserRole.CLIENT)
        return self.role == client_role

    def delete(self, **kwargs):
        if not kwargs.get('hard'):
            self.email = "{}:{}".format(self.email, int(datetime.timestamp(datetime.now())))
            self.save()
        return super().delete(**kwargs)


class Admin(User):
    """Админ"""
    objects = AdminManager()
    def save(self, **kwargs):
        if not self.id:
            self.role = User.UserRole.ADMIN
            self.confirmed_at = datetime.now()
        return super().save(**kwargs)
    class Meta(User.Meta):
        proxy = True
        verbose_name_plural = 'Admin'


class Driver(models.Model):
    """Разработчик"""
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    car_name = models.CharField(max_length=100,null=True)
    car_number = models.CharField(max_length=200,null=True)
    objects = DriverManager
    class Meta(User.Meta):
        verbose_name_plural = 'Driver'


class Client(models.Model):
    """Покупатель"""
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    objects = DriverManager
    class Meta(User.Meta):
        verbose_name_plural = 'Client'

class Code(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    number = models.CharField(max_length=5)

    def save(self,*args,**kwargs):
        self.number = randint(10000,99999)
        super().save(*args,**kwargs)

    class Meta:
        verbose_name_plural = "Code"

    def __str__(self):
        return f"{self.user.username} | {self.number}"