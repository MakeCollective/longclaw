# Generated by Django 3.1.3 on 2021-04-08 05:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0003_auto_20190322_1429'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shippingrate',
            options={'ordering': ['name']},
        ),
    ]
