from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True, default='No description')  # Default value added for description

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=1)
    roles = models.ManyToManyField(Role)
    max_hours_per_week = models.IntegerField()
    can_work_extra = models.BooleanField(default=False)
    rotate_weekends = models.BooleanField(default=False)
    can_work_any_time = models.BooleanField(default=False)
    on_holiday = models.BooleanField(default=False)
    on_sick_leave = models.BooleanField(default=False)
    available_start_time = models.TimeField(null=True, blank=True)
    available_end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Holiday(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return self.name

class Shift(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, default=1) 
    is_sick = models.BooleanField(default=False)

    def __str__(self):
        return f"Shift {self.department} on {self.day_of_week}"

class ShiftRequirement(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)
    shift_start_time = models.TimeField()
    shift_end_time = models.TimeField()
    required_employees = models.IntegerField()

    def __str__(self):
        return f"{self.role} - {self.day_of_week}"

class AttendanceReport(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=50)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.employee} - {self.status} on {self.date}"
