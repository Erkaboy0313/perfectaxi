# Generated by Django 4.2.2 on 2023-12-15 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_rejectreason_order_reject_comment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('assigned', 'Assigned'), ('arrived', 'Arrived'), ('delivering', 'Delivering'), ('delivered', 'Delivered'), ('rejected', 'Rejected')], default='active', max_length=15),
        ),
    ]
