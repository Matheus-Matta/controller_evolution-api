# Generated by Django 4.2.4 on 2024-09-24 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0007_sendmensagem_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='campaign',
            old_name='sent_success',
            new_name='send_success',
        ),
    ]
