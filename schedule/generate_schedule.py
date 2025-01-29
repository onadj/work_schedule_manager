from datetime import datetime, timedelta
from schedule.models import Employee, Shift, ShiftRequirement

def generate_shifts():
    # Preuzmi sve zahtjeve za smjene
    shift_requirements = ShiftRequirement.objects.all()

    for requirement in shift_requirements:
        # Preuzmi sve zaposlenike koji mogu raditi u ovoj smjeni
        available_employees = Employee.objects.filter(
            department=requirement.department,
            roles=requirement.role,
            max_hours_per_week__gt=0  # Možemo dodati dodatne provjere prema uvjetima zaposlenika
        )

        # Dodaj zaposlenike na smjenu dok ne postignemo zahtjevani broj zaposlenika
        for i, employee in enumerate(available_employees):
            if i >= requirement.required_employees:
                break  # Zaustavi kada dostigneš broj potrebnih zaposlenika

            # Dodaj smjenu za zaposlenika
            Shift.objects.create(
                department=requirement.department,
                day_of_week=requirement.day_of_week,
                start_time=requirement.shift_start_time,
                end_time=requirement.shift_end_time,
                employee=employee,
                is_sick=False  # Ovo možemo postaviti prema uvjetima
            )

# Pozovi funkciju za generiranje smjena
if __name__ == "__main__":
    generate_shifts()
