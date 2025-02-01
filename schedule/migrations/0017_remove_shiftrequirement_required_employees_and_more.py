# Generated by Django 5.1.5 on 2025-02-01 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0016_shiftrequirement_total_hours_needed_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shiftrequirement',
            name='required_employees',
        ),
        migrations.AlterField(
            model_name='shiftrequirement',
            name='shift_type',
            field=models.CharField(choices=[('12-12', '12-12'), ('8-14', '8-14'), ('14-20', '14-20')], default='12-12', max_length=10),
        ),
    ]
