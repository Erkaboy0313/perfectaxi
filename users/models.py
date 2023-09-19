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
    
    def __str__(self):
        return f"{self.name} {self.phone}"

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
    """Haydovchi"""

    class DriverStatus(models.TextChoices):
        ACTIVE = 'active'
        BUSY = 'busy'

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    profile_image = models.FileField(null=True)
    car_images = models.ManyToManyField('DocumentImages',related_name='car_images')
    car_tex_passport_images = models.ManyToManyField('DocumentImages',related_name='car_text_images')
    license_images = models.ManyToManyField('DocumentImages',related_name='license_images')
    car_model = models.CharField(max_length=200,null=True)
    status = models.CharField(max_length=20,choices=DriverStatus.choices,default=DriverStatus.ACTIVE)
    car_name = models.CharField(max_length=100,null=True)
    car_number = models.CharField(max_length=200,null=True)
    car_color = models.CharField(max_length=100,null=True)
    car_manufactured_date = models.DateField(null=True)
    car_tex_passport_date = models.DateField(null=True)
    license_date = models.DateField(null=True)
    luggage = models.BooleanField(default=False)
    airconditioner = models.BooleanField(default=False)
    inmark = models.BooleanField(default=False)

    objects = DriverManager

    @property
    def name(self):
        return self.user.name

    def __str__(self):
        return f"{self.user}"

    class Meta(User.Meta):
        verbose_name_plural = 'Drivers'

class Client(models.Model):
    """Покупатель"""

    class PaymentType(models.TextChoices):
        CASH = 'cash'
        CARD = 'card'

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=4,choices=PaymentType.choices,default=PaymentType.CASH)
    rejected_orders = models.PositiveIntegerField(default=0,blank=True)

    objects = DriverManager

    @property
    def order_rejected(self):
        self.rejected_orders += 1
        self.save()

    class Meta(User.Meta):
        verbose_name_plural = 'Client'

    def __str__(self):
        return str(self.user)

class DocumentImages(models.Model):
    image = models.FileField(upload_to='UserDocuments/')


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


