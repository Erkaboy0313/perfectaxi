# Generated by Django 4.2.2 on 2023-10-04 07:01

from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('role', models.CharField(choices=[('client', 'Client'), ('driver', 'Driver'), ('admin', 'Admin')], max_length=20)),
                ('name', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=40, null=True)),
                ('confirmed_at', models.DateTimeField(null=True)),
                ('blocked_at', models.DateTimeField(null=True)),
                ('reason', models.TextField(null=True)),
                ('is_block', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DocumentImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to='UserDocuments/')),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_image', models.FileField(null=True, upload_to='')),
                ('car_model', models.CharField(max_length=200, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('busy', 'Busy')], default='active', max_length=20)),
                ('car_name', models.CharField(max_length=100, null=True)),
                ('car_number', models.CharField(max_length=200, null=True)),
                ('car_color', models.CharField(max_length=100, null=True)),
                ('car_manufactured_date', models.DateField(null=True)),
                ('car_tex_passport_date', models.DateField(null=True)),
                ('license_date', models.DateField(null=True)),
                ('luggage', models.BooleanField(default=False)),
                ('airconditioner', models.BooleanField(default=False)),
                ('inmark', models.BooleanField(default=False)),
                ('car_images', models.ManyToManyField(related_name='car_images', to='users.documentimages')),
                ('car_tex_passport_images', models.ManyToManyField(related_name='car_text_images', to='users.documentimages')),
                ('license_images', models.ManyToManyField(related_name='license_images', to='users.documentimages')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'Drivers',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=5)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Code',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(choices=[('cash', 'Cash'), ('card', 'Card')], default='cash', max_length=4)),
                ('rejected_orders', models.PositiveIntegerField(blank=True, default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'Client',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'Admin',
                'abstract': False,
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('users.user',),
        ),
    ]
