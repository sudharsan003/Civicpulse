# Generated by Django 5.2.2 on 2025-06-22 13:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('civicpulse', '0005_issueimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issue',
            name='image',
        ),
    ]
