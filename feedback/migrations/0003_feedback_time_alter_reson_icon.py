# Generated by Django 4.2.2 on 2023-10-21 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='time',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='reson',
            name='icon',
            field=models.FileField(upload_to='Problems/'),
        ),
    ]
