# Generated by Django 4.2.4 on 2024-09-24 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0009_campaign_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='status',
            field=models.CharField(max_length=15, null=True),
        ),
    ]
