# Generated by Django 5.0.7 on 2024-07-29 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0002_instance_messages_upsert'),
    ]

    operations = [
        migrations.RenameField(
            model_name='instance',
            old_name='messages_upsert',
            new_name='contacts_upsert',
        ),
    ]
