from datetime import datetime
from .models import Department, ShiftRequirement, Employee, Shift, WorkDay
from django.contrib import messages

def generate_shifts(request=None):
    today = datetime.now().date()
    departments = Department.objects.all()  # Osiguraj da se uzmu svi odjeli

    # Prolazimo kroz sve odjele
    for department in departments:
        shift_requirements = ShiftRequirement.objects.filter(department=department)

        # Prolazimo kroz sve zahtjeve za smjene u svakom odjelu
        for shift_requirement in shift_requirements:
            day_of_week = shift_requirement.day_of_week
            start_time = shift_requirement.shift_start_time
            end_time = shift_requirement.shift_end_time
            required_employees = shift_requirement.required_employees

            assigned_employees = Shift.objects.filter(
                department=department,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            ).count()

            if assigned_employees >= required_employees:
                continue  # Ako su smjene već popunjene, preskoči

            # Filtriraj zaposlenike koji mogu raditi
            available_employees = Employee.objects.filter(
                department=department,
                on_holiday=False,
                on_sick_leave=False,
                work_days__name=day_of_week  # Provjeri dostupnost na dan u tjednu
            ).exclude(
                shift__day_of_week=day_of_week,
                shift__start_time=start_time,
                shift__end_time=end_time
            ).distinct()

            if available_employees.count() < (required_employees - assigned_employees):
                # Ako nema dovoljno zaposlenika, obavijestimo
                if request:
                    messages.error(request, f"Nema dovoljno zaposlenika za smjenu {day_of_week} od {start_time} do {end_time} u {department.name}.")
                continue

            # Dodaj zaposlenike na smjenu
            for employee in available_employees:
                assigned_employees += 1

                # Kreiraj smjenu za zaposlenika
                Shift.objects.create(
                    department=department,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                    employee=employee
                )

                if assigned_employees >= required_employees:
                    break  # Ako smo popunili dovoljno smjena, prestanimo dodavati zaposlenike

            # Ako su smjene popunjene, nastavi dalje s idućim zahtjevima
            if assigned_employees >= required_employees:
                continue

    return True  # Funkcija uspješno završena
