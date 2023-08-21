# Generated by Django 4.2.2 on 2023-08-01 12:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0009_alter_client_payment_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_number', models.CharField(max_length=35, null=True)),
                ('start_adress', models.CharField(max_length=255, null=True)),
                ('start_point', models.CharField(max_length=40, null=True)),
                ('ordered_time', models.DateTimeField(auto_now_add=True)),
                ('taken_time', models.DateTimeField(null=True)),
                ('rejected_time', models.DateTimeField(null=True)),
                ('distance', models.FloatField()),
                ('price', models.FloatField()),
                ('payment_type', models.CharField(max_length=4, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('delivering', 'Delivering'), ('delivered', 'Delivered'), ('rejected', 'Rejected')], max_length=15)),
                ('reject_reason', models.TextField(null=True)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.client')),
                ('driver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.driver')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('cost', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.CharField(max_length=40, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='order',
            name='services',
            field=models.ManyToManyField(to='order.services'),
        ),
    ]
