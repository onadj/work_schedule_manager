# Generated by Django 5.1.5 on 2025-02-02 13:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0022_employee_can_work_partial_day'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='can_work_partial_day',
        ),
    ]
