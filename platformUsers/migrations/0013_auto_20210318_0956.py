# Generated by Django 3.1.7 on 2021-03-18 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("platformUsers", "0012_auto_20210305_1346"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="ph_number",
            field=models.IntegerField(null=True, unique=True),
        ),
    ]
