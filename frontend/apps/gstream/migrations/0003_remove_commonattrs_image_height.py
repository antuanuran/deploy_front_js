# Generated by Django 4.2.5 on 2024-08-04 11:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("gstream", "0002_alter_cameraattrs_framerate_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="commonattrs",
            name="image_height",
        ),
    ]
