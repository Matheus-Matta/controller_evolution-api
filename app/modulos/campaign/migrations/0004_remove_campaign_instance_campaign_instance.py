# Generated by Django 4.2.4 on 2024-09-20 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0007_alter_instance_public_name'),
        ('campaign', '0003_alter_campaign_total_numbers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='instance',
        ),
        migrations.AddField(
            model_name='campaign',
            name='instance',
            field=models.ManyToManyField(to='instance.instance'),
        ),
    ]
