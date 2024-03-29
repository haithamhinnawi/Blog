# Generated by Django 4.2.7 on 2023-12-19 11:57

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blogs', '0015_alter_blocks_blocked_until_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blocks',
            name='blocked_until',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 29, 11, 57, 22, 692427, tzinfo=datetime.timezone.utc), verbose_name='Blocked until'),
        ),
        migrations.CreateModel(
            name='UserBadgesTracker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posts_counter', models.PositiveIntegerField(default=0)),
                ('user_likes_counter', models.PositiveIntegerField(default=0)),
                ('user_posts_likes_counter', models.PositiveIntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Badges',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('badge', models.CharField(max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
