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
            name='Reson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('problem', 'Problem'), ('comfort', 'Comfort')], max_length=20, null=True)),
                ('icon', models.ImageField(upload_to='Problems/')),
                ('name', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark', models.PositiveIntegerField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.client')),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.driver')),
                ('resons', models.ManyToManyField(to='feedback.reson')),
            ],
        ),
    ]
