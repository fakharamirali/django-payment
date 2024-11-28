# Generated by Django 5.1.2 on 2024-11-07 03:49

import payment.registry
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payportal',
            name='api_key',
            field=models.CharField(max_length=255, verbose_name='API Key'),
        ),
        migrations.AlterField(
            model_name='payportal',
            name='backend',
            field=models.CharField(choices=payment.registry.get_choices, max_length=512, verbose_name='Backend'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_id',
            field=models.CharField(max_length=255, null=True, verbose_name='Transaction ID'),
        ),
    ]