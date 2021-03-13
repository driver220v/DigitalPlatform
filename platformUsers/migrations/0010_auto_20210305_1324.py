# Generated by Django 3.1.7 on 2021-03-05 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("platformUsers", "0009_auto_20210305_1314"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="avatar",
            field=models.ImageField(upload_to="profile_pictures"),
        ),
        migrations.AlterField(
            model_name="profile",
            name="user_type",
            field=models.CharField(
                choices=[("student", "student"), ("teacher", "teacher")], max_length=10
            ),
        ),
    ]
