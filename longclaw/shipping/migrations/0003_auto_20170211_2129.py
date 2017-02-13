# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-11 21:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0030_index_on_pagerevision_created_at'),
        ('shipping', '0002_auto_20170211_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingcountry',
            name='page_ptr',
            field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='wagtailcore.Page'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='shippingrate',
            name='shipping_country',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipping_rates', to='shipping.ShippingCountry'),
        ),
    ]
