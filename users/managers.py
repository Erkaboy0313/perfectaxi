from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from PerfectTaxi.exceptions import BaseAPIException
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from dotenv import dotenv_values
env_conf = dotenv_values('.env')

class BaseManager(BaseUserManager):
    def exist_user(self, data):
        queryset = get_user_model().objects
        if data.get('user_id', None):
            queryset = queryset.filter(~Q(id=data.get('user_id')))
        return queryset.filter(phone=data['phone'],role=data['role']).exists()

class AdminManager(BaseManager):
    def get_queryset(self):
        return super().get_queryset().filter(role=self.model.UserRole.ADMIN)

    def create_superuser(self,phone, name='admin', password=None, *args, **kwargs):
        if not password:
            password = env_conf.get('DJANGO_SUPERUSER_PASSWORD')
        return get_user_model().objects.create(
            role=self.model.UserRole.ADMIN,
            phone=phone,
            name=name,
            password=make_password(password),
            is_staff=True,
            is_superuser=True,
            is_active=True,
            confirmed_at=datetime.now(),
            *args,
            **kwargs
        )
    
    def get_admins_emails(self):
        #TODO: нужно ли учитывать заблокированных админов?
        admins_emails = self.get_queryset().values_list('email', flat=True)
        return list(admins_emails)


class UserManager(BaseManager):

    def create_user(self, role, phone, name, *args, **kwargs):
        return get_user_model().objects.create(
            phone=phone,
            name=name,
            role=role,
            *args,
            **kwargs
        )
    
    def create_superuser(self,phone, name='admin', password=None, *args, **kwargs):
        if not password:
            password = env_conf.get('DJANGO_SUPERUSER_PASSWORD')
        return get_user_model().objects.create(
            role=self.model.UserRole.ADMIN,
            phone=phone,
            name=name,
            password=make_password(password),
            is_staff=True,
            is_superuser=True,
            is_active=True,
            confirmed_at=datetime.now(),
            *args,
            **kwargs
        )

    def get_users_queryset(self):
        return super().get_queryset().filter(~Q(role=self.model.UserRole.ADMIN))

    def get_companies_queryset(self):
        return self.get_users_queryset().select_related('notification_settings').filter(confirmed_at__isnull=False)

    def get_requests_queryset(self):
        return self.get_users_queryset().filter(confirmed_at__isnull=True)

    def get_request(self, pk):
        try:
            return self.get_requests_queryset().get(id=pk)
        except ObjectDoesNotExist:
            raise BaseAPIException('Заявка не найдена')

class DriverManager(BaseManager):
    def get_queryset(self):
        return super().get_queryset().filter(role=self.model.UserRole.DRIVER)
