# Generated by Django 4.2.2 on 2024-06-03 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driver',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('busy', 'Busy'), ('blocked', 'Block')], default='busy', max_length=20),
        ),
    ]