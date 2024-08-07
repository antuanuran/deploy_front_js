# Generated by Django 4.2.5 on 2024-08-04 06:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("v_superuser", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        choices=[
                            ("H264-1", "H264 1"),
                            ("H264-2", "H264 2"),
                            ("H264-3", "H264 3"),
                        ],
                        max_length=50,
                    ),
                ),
            ],
        ),
    ]
