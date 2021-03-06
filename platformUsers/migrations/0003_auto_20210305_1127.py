# Generated by Django 3.1.7 on 2021-03-05 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("platformUsers", "0002_auto_20210305_1058"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="avatar",
            field=models.ImageField(upload_to="profile_pictures"),
        ),
        migrations.AlterField(
            model_name="profile",
            name="ph_number",
            field=models.IntegerField(null=True),
        ),
    ]
