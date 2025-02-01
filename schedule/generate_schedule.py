from datetime import datetime
from django.contrib import messages
from .models import Department, Employee, WorkDay, Shift, FlexibleShift

def generate_shifts(request=None):
    today = datetime.now().date()
    departments = Department.objects.all()

    for department in departments:
        flexible_shifts = FlexibleShift.objects.filter(department=department)

        for shift in flexible_shifts:
            start_time = max(shift.shift_start_time, department.work_start_time)
            end_time = min(shift.shift_end_time, department.work_end_time)

            for work_day in WorkDay.objects.all():
                day_of_week = work_day.name
                required_employees = 2  # Možeš dodati custom logiku ako se broj zaposlenika po smjeni mijenja

                assigned_employees = Shift.objects.filter(
                    department=department,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time
                ).count()

                if assigned_employees >= required_employees:
                    continue  

                available_employees = Employee.objects.filter(
                    department=department,
                    on_holiday=False,
                    on_sick_leave=False,
                    work_days=work_day
                ).exclude(
                    shift__day_of_week=day_of_week,
                    shift__start_time=start_time,
                    shift__end_time=end_time
                ).distinct()

                if available_employees.count() < (required_employees - assigned_employees):
                    if request:
                        messages.error(request, f"Nema dovoljno zaposlenika za smjenu {day_of_week} od {start_time} do {end_time} u {department.name}.")
                    continue

                for employee in available_employees:
                    assigned_employees += 1
                    Shift.objects.create(
                        department=department,
                        day_of_week=day_of_week,
                        start_time=start_time,
                        end_time=end_time,
                        employee=employee
                    )

                    if assigned_employees >= required_employees:
                        break  

    return True  
