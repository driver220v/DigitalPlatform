# Generated by Django 3.1.7 on 2021-03-05 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("platformUsers", "0003_auto_20210305_1127"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="user_type",
            field=models.CharField(max_length=10, null=True),
        ),
    ]
