# Generated by Django 5.0.6 on 2024-06-18 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_remove_shippingaddress_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeruser',
            name='phone',
            field=models.CharField(blank=True, null=True),
        ),
    ]
