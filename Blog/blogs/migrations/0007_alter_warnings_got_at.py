# Generated by Django 4.2.7 on 2023-12-06 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0006_warnings_bad_words_count_delete_customuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warnings',
            name='got_at',
            field=models.DateTimeField(null=True, verbose_name='Got at'),
        ),
    ]
