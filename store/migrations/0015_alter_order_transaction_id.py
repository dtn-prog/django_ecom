# Generated by Django 5.0.6 on 2024-06-28 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_alter_customeruser_phone_alter_order_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(default='a0dade1a-f6b8-437c-872b-1d4eee9d5be4', max_length=255, null=True, unique=True),
        ),
    ]
