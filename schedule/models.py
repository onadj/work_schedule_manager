from django.db import models
from django.contrib.auth.models import User  # For admin users

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    department = models.ManyToManyField(Department, related_name='employees')
    roles = models.ManyToManyField(Role, related_name='employees')  # Multiple roles
    max_hours_per_week = models.PositiveIntegerField(default=40)
    can_work_extra = models.BooleanField(default=False)
    rotate_weekends = models.BooleanField(default=False)
    avoid_holidays = models.BooleanField(default=False)
    total_annual_leave = models.PositiveIntegerField(default=20)
    used_annual_leave = models.PositiveIntegerField(default=0)
    sick_days = models.PositiveIntegerField(default=0)
    unauthorized_absences = models.PositiveIntegerField(default=0)

    # New fields
    can_work_any_time = models.BooleanField(default=False, help_text="Can this employee work at any time, including night shifts?")
    available_start_time = models.TimeField(null=True, blank=True, help_text="Earliest available time to work (leave blank for 24-hour availability).")
    available_end_time = models.TimeField(null=True, blank=True, help_text="Latest available time to work (leave blank for 24-hour availability).")

    # Absences
    on_holiday = models.BooleanField(default=False, help_text="Is the employee currently on holiday?")
    on_sick_leave = models.BooleanField(default=False, help_text="Is the employee currently on sick leave?")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Holiday(models.Model):
    name = models.CharField(max_length=100, unique=True)
    date = models.DateField(unique=True)

    def __str__(self):
        return self.name

class ShiftRequirement(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='shift_requirements')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='shift_requirements')
    day_of_week = models.CharField(
        max_length=10,
        choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
                 ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')],
    )
    shift_start_time = models.TimeField()
    shift_end_time = models.TimeField()
    required_employees = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.department.name} - {self.role.name} on {self.day_of_week} ({self.shift_start_time} - {self.shift_end_time})"

class Shift(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='shifts')
    day_of_week = models.CharField(
        max_length=10,
        choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
                 ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')],
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='shifts')
    is_sick = models.BooleanField(default=False)
    replacement_employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replacement_shifts'
    )

    def __str__(self):
        return f"{self.department.name} - {self.day_of_week} ({self.start_time} - {self.end_time})"

class AttendanceReport(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_reports')
    date = models.DateField()
    status = models.CharField(
        max_length=50,
        choices=[('Present', 'Present'), ('Sick', 'Sick'), ('Absent', 'Absent'), ('On Leave', 'On Leave')],
    )
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - {self.date}"
