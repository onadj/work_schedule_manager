from datetime import datetime
from django.db.models import Count

def generate_shifts():
    today = datetime.now().date()
    departments = Department.objects.all()

    for department in departments:
        shift_requirements = ShiftRequirement.objects.filter(department=department)

        for shift_requirement in shift_requirements:
            day_of_week = shift_requirement.day_of_week
            start_time = shift_requirement.shift_start_time
            end_time = shift_requirement.shift_end_time
            required_employees = shift_requirement.required_employees

            # Provjera broja već dodijeljenih zaposlenika
            assigned_employees = Shift.objects.filter(
                department=department,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            ).count()

            if assigned_employees >= required_employees:
                continue  # Preskoči ako su već svi zaposlenici dodijeljeni

            # Dohvati sve dostupne zaposlenike koji nisu na odmoru ili bolovanju
            available_employees = Employee.objects.filter(
                department=department,
                on_holiday=False,
                on_sick_leave=False
            ).exclude(
                shifts__day_of_week=day_of_week,
                shifts__start_time=start_time,
                shifts__end_time=end_time
            ).distinct()

            for employee in available_employees:
                if assigned_employees >= required_employees:
                    break  # Ako je broj zaposlenika dosegnut, prekini petlju

                # Dodjela smjene zaposleniku
                Shift.objects.create(
                    department=department,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                    employee=employee
                )
                assigned_employees += 1  # Ažuriraj broj dodijeljenih zaposlenika