from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    max_hours_per_week = models.PositiveIntegerField(default=40)

    def __str__(self):
        return self.name

class Employee(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('nurse', 'Nurse'),
        ('activities', 'Activities'),
        ('hca', 'Healthcare Assistant'),
        ('chef', 'Chef'),
        ('kitchen_assistant', 'Kitchen Assistant'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    max_hours_per_week = models.PositiveIntegerField(default=40)
    is_flexible = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"