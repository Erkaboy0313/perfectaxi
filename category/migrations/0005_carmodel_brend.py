# Generated by Django 4.2.2 on 2025-01-22 06:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0004_carmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='carmodel',
            name='brend',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='category.carbrend'),
        ),
    ]