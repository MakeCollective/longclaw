# Generated by Django 3.1.3 on 2021-06-29 01:15

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
        ('orders', '0002_order_total_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='base_product_id',
            field=models.IntegerField(null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='date_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_variant_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_variant_price',
            field=models.DecimalField(decimal_places=2, null=True, max_digits=12),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_variant_ref',
            field=models.CharField(null=True, max_length=32),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_variant_title',
            field=models.CharField(null=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.productvariant'),
        ),
    ]
