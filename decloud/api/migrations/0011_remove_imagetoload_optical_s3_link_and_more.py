# Generated by Django 5.1.5 on 2025-04-23 18:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_imagetoload_delete_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagetoload',
            name='optical_s3_link',
        ),
        migrations.RemoveField(
            model_name='imagetoload',
            name='sar_s3_link',
        ),
    ]
