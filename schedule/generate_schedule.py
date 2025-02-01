from datetime import datetime
from .models import Department, ShiftRequirement, Employee, Shift, WorkDay

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

            assigned_employees = Shift.objects.filter(
                department=department,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            ).count()

            if assigned_employees >= required_employees:
                continue

            # Filtriraj zaposlenike na temelju svih uvjeta
            available_employees = Employee.objects.filter(
                department=department,
                on_holiday=False,  # Provjeri da nisu na odmoru
                on_sick_leave=False,  # Provjeri da nisu na bolovanju
                work_days__name=day_of_week  # Provjeri dostupnost na dan u tjednu
            ).exclude(
                shift__day_of_week=day_of_week,
                shift__start_time=start_time,
                shift__end_time=end_time
            ).distinct()

            for employee in available_employees:
                # Dodatni uvjeti: maksimalne sate i mogućnost rada dodatnih smjena
                if (employee.max_hours_per_week and employee.max_hours_per_week <= assigned_employees * 8):
                    continue  # Ako je dostigao maksimalne sate, preskoči ga

                if not employee.can_work_extra and assigned_employees >= required_employees:
                    continue  # Ako ne može raditi dodatne smjene, preskoči ga

                if assigned_employees >= required_employees:
                    break

                # Kreiraj smjenu za dostupnog zaposlenika
                Shift.objects.create(
                    department=department,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                    employee=employee
                )
                assigned_employees += 1
