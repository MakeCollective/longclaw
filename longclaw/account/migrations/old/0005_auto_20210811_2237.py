# Generated by Django 3.1.3 on 2021-08-11 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_paymentmethod_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='status',
            field=models.IntegerField(choices=[(1, 'Active'), (2, 'Deactivate'), (3, 'Invalid'), (4, 'Expired')], default=1, help_text='Status to show if the PaymentMethod is active/deactive or otherwise'),
        ),
    ]
