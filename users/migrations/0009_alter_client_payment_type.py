# Generated by Django 4.2.2 on 2023-08-01 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_rename_immark_driver_inmark'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='payment_type',
            field=models.CharField(choices=[('cash', 'Cash'), ('card', 'Card')], default='cash', max_length=4),
        ),
    ]
