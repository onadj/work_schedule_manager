from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True, default='No description')
    work_start_time = models.TimeField(default="08:00")  # Default vrijeme, može se mijenjati
    work_end_time = models.TimeField(default="18:00")

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class WorkDay(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    name = models.CharField(max_length=10, choices=DAYS_OF_WEEK, unique=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=1)
    roles = models.ManyToManyField(Role)
    max_hours_per_week = models.IntegerField()
    max_hours_per_day = models.IntegerField(default=8)
    preferred_shift_length = models.IntegerField(default=8)
    can_work_extra = models.BooleanField(default=False)
    rotate_weekends = models.BooleanField(default=False)
    avoid_holidays = models.BooleanField(default=False)
    can_work_any_time = models.BooleanField(default=False)
    can_work_night_shift = models.BooleanField(default=False)  # Dodano polje za noćne smjene
    on_holiday = models.BooleanField(default=False)
    on_sick_leave = models.BooleanField(default=False)
    total_annual_leave = models.IntegerField(default=0)
    used_annual_leave = models.IntegerField(default=0)
    sick_days = models.IntegerField(default=0)
    unauthorized_absences = models.IntegerField(default=0)
    available_start_time = models.TimeField(null=True, blank=True)
    available_end_time = models.TimeField(null=True, blank=True)
    available_days = models.ManyToManyField(WorkDay, blank=True)  # Dani kada je zaposlenik dostupan

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class ShiftRequirement(models.Model):
    SHIFT_TYPES = [
        ('08-20', '08-20'),  # Dnevna smjena (12 sati)
        ('08-14', '08-14'),  # Jutarnja smjena (6 sati)
        ('14-20', '14-20'),  # Popodnevna smjena (6 sati)
        ('20-08', '20-08'),  # Noćna smjena (12 sati)
    ]
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)
    day_of_week = models.CharField(max_length=10, choices=WorkDay.DAYS_OF_WEEK)
    shift_type = models.CharField(max_length=10, choices=SHIFT_TYPES, default='08-20')
    total_hours_needed = models.IntegerField(default=24)  # Ukupan broj sati potrebnih za dan

    def __str__(self):
        return f"{self.department.name} - {self.day_of_week} ({self.shift_type})"

class FlexibleShift(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    shift_start_time = models.TimeField()
    shift_end_time = models.TimeField()

    def __str__(self):
        return f"{self.department.name}: {self.shift_start_time} - {self.shift_end_time}"

class Shift(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=WorkDay.DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='shift')

    def __str__(self):
        return f"{self.employee} - {self.day_of_week} ({self.start_time} - {self.end_time})"

class AttendanceReport(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=50)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.employee} - {self.status} on {self.date}"

class Holiday(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return self.name