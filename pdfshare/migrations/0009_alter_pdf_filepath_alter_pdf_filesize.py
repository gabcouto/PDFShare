# Generated by Django 4.0.4 on 2022-04-18 23:49

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdfshare', '0008_transacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdf',
            name='filepath',
            field=models.FileField(upload_to='foo/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
        migrations.AlterField(
            model_name='pdf',
            name='filesize',
            field=models.IntegerField(default=0, max_length=250),
        ),
    ]
