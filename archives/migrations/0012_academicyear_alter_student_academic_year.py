# Generated by Django 5.0.6 on 2024-07-27 20:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archives', '0011_projecttype_mentor_staff_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starting_year', models.DateField()),
                ('ending_year', models.DateField()),
            ],
        ),
        migrations.AlterField(
            model_name='student',
            name='academic_year',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='archives.academicyear'),
        ),
    ]