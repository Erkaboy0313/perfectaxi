# Generated by Django 4.2.2 on 2024-02-16 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver', models.CharField(choices=[('driver', 'Driver'), ('client', 'Client')], max_length=20)),
                ('message', models.TextField()),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('driver', 'Driver'), ('client', 'Client'), ('all', 'All'), ('personal', 'Personal')], max_length=20)),
                ('message', models.TextField()),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TermsAndConditions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('file', models.FileField(upload_to='TermsAndConditions/')),
                ('time', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
