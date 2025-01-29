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

            # Logic to assign employees to shifts
            # Get all employees available to work this shift
            employees = Employee.objects.filter(department=department)
            for employee in employees:
                if employee.can_work_any_time:
                    # Assign this employee to any shift
                    Shift.objects.create(
                        department=department,
                        day_of_week=day_of_week,
                        start_time=start_time,
                        end_time=end_time,
                        employee=employee
                    )
                elif Shift.objects.filter(employee=employee, day_of_week=day_of_week).count() < required_employees:
                    # Assign the employee to the shift only if they have not been assigned yet
                    Shift.objects.create(
                        department=department,
                        day_of_week=day_of_week,
                        start_time=start_time,
                        end_time=end_time,
                        employee=employee
                    )
