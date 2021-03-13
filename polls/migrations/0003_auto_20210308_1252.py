# Generated by Django 3.1.7 on 2021-03-08 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0002_auto_20210308_1225"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pollquestionanswer",
            name="user_choice",
        ),
        migrations.AddField(
            model_name="pollquestionanswer",
            name="is_correct",
            field=models.BooleanField(default=False),
        ),
    ]