# Generated by Django 4.2.7 on 2023-11-29 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='date published'),
        ),
    ]
