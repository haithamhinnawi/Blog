# Generated by Django 4.2.7 on 2023-12-10 08:56

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blogs', '0011_alter_blocks_blocked_until_postsread'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blocks',
            name='blocked_until',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 20, 8, 56, 2, 637824, tzinfo=datetime.timezone.utc), verbose_name='Blocked until'),
        ),
        migrations.AlterField(
            model_name='postsread',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
