from datetime import datetime, time, timedelta
from django.contrib import messages
from .models import Employee, Shift, WorkDay, ShiftRequirement

def generate_shifts(request):
    today = datetime.now().date()
    work_days = WorkDay.objects.all()  # Svi radni dani (Monday, Tuesday, ...)

    # Svi zaposlenici s početnim radnim satima postavljenim na 0
    employee_hours = {employee.id: 0 for employee in Employee.objects.all()}

    # Definiranje smjena
    shift_options = {
        '08-20': (time(8, 0), time(20, 0), 12),
        '08-14': (time(8, 0), time(14, 0), 6),
        '14-20': (time(14, 0), time(20, 0), 6),
        '20-08': (time(20, 0), time(8, 0), 12),  # Noćna smjena
    }

    for work_day in work_days:
        for shift_type, (start, end, shift_hours) in shift_options.items():
            start_time = datetime.combine(today, start)
            end_time = datetime.combine(today, end)
            if shift_type == '20-08':
                end_time += timedelta(days=1)  # Noćna smjena prelazi u sljedeći dan

            # Dohvati zaposlenike koji mogu raditi taj dan
            available_employees = Employee.objects.filter(
                available_days__name=work_day.name,
                on_holiday=False,
                on_sick_leave=False
            ).exclude(
                id__in=Shift.objects.filter(start_time__lte=end_time.time(), end_time__gte=start_time.time()).values_list('employee', flat=True)
            )

            # Dodjeljivanje zaposlenika smjeni
            for employee in available_employees:
                if (
                    employee_hours[employee.id] + shift_hours <= employee.max_hours_per_week
                    and (employee.available_start_time is None or start >= employee.available_start_time)
                    and (employee.available_end_time is None or end <= employee.available_end_time)
                ):
                    Shift.objects.create(
                        employee=employee,
                        department=employee.department,
                        start_time=start_time.time(),
                        end_time=end_time.time(),
                        day_of_week=work_day.name,
                        shift_type=shift_type,
                        hours=shift_hours
                    )
                    employee_hours[employee.id] += shift_hours
                    break  # Nakon što dodijelimo zaposlenika, idemo na sljedeću smjenu

        # Ako nema dovoljno zaposlenika za određeni dan, prikazi upozorenje
        required_shifts = ShiftRequirement.objects.filter(day_of_week=work_day.name).count()
        assigned_shifts = Shift.objects.filter(day_of_week=work_day.name).count()

        if assigned_shifts < required_shifts:
            messages.warning(request, f"Nedovoljno zaposlenika za {work_day.name}!")

    messages.success(request, "Smjene su uspješno generirane!")