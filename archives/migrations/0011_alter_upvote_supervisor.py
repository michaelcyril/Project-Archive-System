# Generated by Django 5.0.6 on 2024-06-30 23:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archives', '0010_remove_upvote_user_upvote_supervisor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upvote',
            name='supervisor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='archives.staff'),
        ),
    ]
