from datetime import datetime, time
from django.contrib import messages
from .models import Department, Employee, WorkDay, Shift, ShiftRequirement

def generate_shifts(request=None):
    today = datetime.now().date()
    requirements = ShiftRequirement.objects.all()

    # Inicijaliziraj praćenje sati po zaposleniku i po danu
    employee_hours = {employee.id: 0 for employee in Employee.objects.all()}
    day_hours = {}  # Praćenje ukupnih sati po danu

    for requirement in requirements:
        department = requirement.department
        role = requirement.role
        day_of_week = requirement.day_of_week
        shift_type = requirement.shift_type
        total_hours_needed = requirement.total_hours_needed
        night_shift_hours_needed = requirement.night_shift_hours_needed

        # Inicijaliziraj praćenje sati za dan ako već nije postavljeno
        if day_of_week not in day_hours:
            day_hours[day_of_week] = 0

        # Pronađi dostupne zaposlenike
        available_employees = Employee.objects.filter(
            department=department,
            roles=role,
            available_days__name=day_of_week,
            on_holiday=False,
            on_sick_leave=False,
        )

        # Ako je noćna smjena, filtriraj samo zaposlenike koji mogu raditi noćne smjene
        if shift_type == '20-08':
            available_employees = available_employees.filter(can_work_night_shift=True)

        # Sortiraj zaposlenike po broju dodijeljenih sati (najmanje iskorišteni prvi)
        available_employees = sorted(
            available_employees,
            key=lambda emp: employee_hours[emp.id]
        )

        # Odredi početno i završno vrijeme smjene
        if shift_type == '08-20':
            start_time = time(8, 0)
            end_time = time(20, 0)
            shift_hours = 12
        elif shift_type == '08-14':
            start_time = time(8, 0)
            end_time = time(14, 0)
            shift_hours = 6
        elif shift_type == '14-20':
            start_time = time(14, 0)
            end_time = time(20, 0)
            shift_hours = 6
        elif shift_type == '20-08':
            start_time = time(20, 0)
            end_time = time(8, 0)
            shift_hours = night_shift_hours_needed  # Koristimo ručno unesene sate za noćne smjene
        else:
            continue  # Ako je nepoznat tip smjene, preskoči

        # Dodijeli smjene
        for employee in available_employees:
            # Provjeri da li je ukupan broj sati za dan već ispunjen
            if day_hours[day_of_week] >= total_hours_needed:
                break

            # Provjeri maksimalne sate tjedno i dnevno
            if (
                employee_hours[employee.id] + shift_hours <= employee.max_hours_per_week
                and shift_hours <= employee.max_hours_per_day
            ):
                Shift.objects.create(
                    department=department,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                    employee=employee,
                )
                day_hours[day_of_week] += shift_hours
                employee_hours[employee.id] += shift_hours

        # Ako nema dovoljno zaposlenika, prikaži upozorenje
        if day_hours[day_of_week] < total_hours_needed and request:
            messages.warning(
                request,
                f"Nema dovoljno zaposlenika za pokriti {total_hours_needed} sati za {day_of_week} u odjelu {department.name}."
            )

    if request:
        messages.success(request, "Smjene su uspješno generirane!")
    return True