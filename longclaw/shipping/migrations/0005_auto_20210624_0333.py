# Generated by Django 3.1.3 on 2021-06-24 03:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0004_auto_20210408_0530'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name': 'Address', 'verbose_name_plural': 'Addresses'},
        ),
    ]
