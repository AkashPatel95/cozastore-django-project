# Generated by Django 4.2.5 on 2023-11-28 03:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_cart'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='product_decription',
            new_name='product_description',
        ),
    ]
