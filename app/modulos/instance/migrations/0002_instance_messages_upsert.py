# Generated by Django 5.0.7 on 2024-07-29 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='messages_upsert',
            field=models.BooleanField(default=False),
        ),
    ]
