from datetime import datetime
from .models import Department, ShiftRequirement, Employee, Shift

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

            # Provjera koliko je zaposlenika već dodijeljeno toj smjeni
            assigned_employees = Shift.objects.filter(
                department=department,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            ).count()

            if assigned_employees >= required_employees:
                continue  # Ako je broj zaposlenika već popunjen, preskoči

            # Dohvati zaposlenike koji nisu na odmoru/bolovanju i nisu već raspoređeni na istu smjenu
            available_employees = Employee.objects.filter(
                department=department,
                on_holiday=False,
                on_sick_leave=False
            ).exclude(
                shift__day_of_week=day_of_week,
                shift__start_time=start_time,
                shift__end_time=end_time
            ).distinct()

            for employee in available_employees:
                if assigned_employees >= required_employees:
                    break  # Ako je popunjen broj zaposlenika, prekini petlju

                # Kreiranje smjene za zaposlenika
                Shift.objects.create(
                    department=department,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                    employee=employee
                )
                assigned_employees += 1  # Ažuriranje broja zaposlenika
