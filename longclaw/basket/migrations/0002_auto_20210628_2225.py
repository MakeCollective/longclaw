# Generated by Django 3.1.3 on 2021-06-28 22:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
        ('basket', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basketitem',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.productvariant'),
        ),
    ]
