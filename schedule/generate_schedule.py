from datetime import datetime, time, timedelta
from django.contrib import messages
from .models import Employee, Shift, WorkDay, ShiftRequirement

def generate_shifts(request):
    today = datetime.now().date()
    work_days = WorkDay.objects.all()
    
    # Svi zaposlenici s početnim radnim satima postavljenim na 0 i zadnjim radnim vremenom
    employee_hours = {employee.id: {'hours': 0, 'last_end_time': None, 'last_day': None} for employee in Employee.objects.all()}
    
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

            available_employees = Employee.objects.filter(
                available_days__name=work_day.name,
                on_holiday=False,
                on_sick_leave=False
            )
            
            for employee in available_employees:
                # Provjera je li zaposlenik već dodijeljen smjeni na taj dan
                existing_shift = Shift.objects.filter(
                    employee=employee,
                    day_of_week=work_day.name
                ).exists()
                
                if existing_shift:
                    continue  # Preskoči zaposlenika ako je već dodijeljen smjeni za taj dan

                last_shift_end = employee_hours[employee.id]['last_end_time']
                last_shift_day = employee_hours[employee.id]['last_day']
                
                # Provjera da zaposlenik ne radi odmah nakon smjene isti dan
                if last_shift_end and last_shift_day == work_day.name:
                    if last_shift_end > start:
                        continue  # Preskoči ovog zaposlenika
                
                if (
                    employee_hours[employee.id]['hours'] + shift_hours <= employee.max_hours_per_week
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
                    
                    # Ažuriraj evidenciju radnih sati i zadnjeg završetka smjene
                    employee_hours[employee.id]['hours'] += shift_hours
                    employee_hours[employee.id]['last_end_time'] = end
                    employee_hours[employee.id]['last_day'] = work_day.name
                    break
        
        # Provjera da li su ispunjeni zahtjevi smjena
        required_shifts = ShiftRequirement.objects.filter(day_of_week=work_day.name).count()
        assigned_shifts = Shift.objects.filter(day_of_week=work_day.name).count()
        
        if assigned_shifts < required_shifts:
            messages.warning(request, f"Nedovoljno zaposlenika za {work_day.name}!")
    
    # Ispis ukupnih sati po zaposleniku
    for employee_id, data in employee_hours.items():
        employee = Employee.objects.get(id=employee_id)
        messages.info(request, f"{employee.first_name} {employee.last_name} ima ukupno {data['hours']} radnih sati ovaj tjedan.")
    
    messages.success(request, "Smjene su uspješno generirane!")
