# Generated by Django 4.2.7 on 2023-12-06 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0005_alter_customuser_options_alter_customuser_managers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='warnings',
            name='bad_words_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
