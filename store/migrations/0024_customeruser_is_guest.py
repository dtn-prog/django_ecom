# Generated by Django 5.0.6 on 2024-07-04 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0023_alter_customeruser_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeruser',
            name='is_guest',
            field=models.BooleanField(default=False),
        ),
    ]
