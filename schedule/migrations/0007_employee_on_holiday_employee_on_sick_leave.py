# Generated by Django 5.1.5 on 2025-01-30 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0006_remove_employee_work_end_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='on_holiday',
            field=models.BooleanField(default=False, help_text='Is the employee currently on holiday?'),
        ),
        migrations.AddField(
            model_name='employee',
            name='on_sick_leave',
            field=models.BooleanField(default=False, help_text='Is the employee currently on sick leave?'),
        ),
    ]
