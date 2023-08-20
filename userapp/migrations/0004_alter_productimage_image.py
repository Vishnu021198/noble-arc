# Generated by Django 4.2.4 on 2023-08-17 13:10

from django.db import migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0003_productimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=image_cropping.fields.ImageCropField(blank=True, null=True, upload_to='photos/product'),
        ),
    ]