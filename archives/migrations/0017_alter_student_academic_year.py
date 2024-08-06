# Generated by Django 5.0.6 on 2024-08-06 08:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archives', '0016_remove_student_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='academic_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='archives.academicyear'),
        ),
    ]
