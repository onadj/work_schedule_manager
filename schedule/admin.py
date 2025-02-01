from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django import forms
from datetime import datetime, timedelta

from .models import Employee, Department, Role, Holiday, Shift, AttendanceReport, ShiftRequirement
from .generate_schedule import generate_shifts  # Provjeri da funkcija ispravno radi

class DateRangeFilter(SimpleListFilter):
    title = _('date range')
    parameter_name = 'date_range'

    def lookups(self, request, model_admin):
        return (
            ('this_week', _('This Week')),
            ('last_week', _('Last Week')),
            ('last_month', _('Last Month')),
            ('custom', _('Custom Date Range')),
        )

    def queryset(self, request, queryset):
        today = datetime.now().date()
        if self.value() == 'this_week':
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            return queryset.filter(date__range=[start_of_week, end_of_week])
        elif self.value() == 'last_week':
            start_of_week = today - timedelta(days=today.weekday() + 7)
            end_of_week = start_of_week + timedelta(days=6)
            return queryset.filter(date__range=[start_of_week, end_of_week])
        elif self.value() == 'last_month':
            start_of_month = today.replace(day=1) - timedelta(days=1)
            start_of_month = start_of_month.replace(day=1)
            end_of_month = start_of_month.replace(month=start_of_month.month + 1) - timedelta(days=1)
            return queryset.filter(date__range=[start_of_month, end_of_month])
        elif self.value() == 'custom':
            pass
        return queryset

class CustomDateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.SelectDateWidget())
    end_date = forms.DateField(widget=forms.SelectDateWidget())

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'max_hours_per_week', 'can_work_extra', 'rotate_weekends', 'can_work_any_time', 'on_holiday', 'on_sick_leave')
    list_filter = ('roles', 'department', 'can_work_extra', 'rotate_weekends', 'can_work_any_time', 'on_holiday', 'on_sick_leave')
    search_fields = ('first_name', 'last_name')
    ordering = ('last_name',)

    filter_horizontal = ('roles',)  # Only keep this for many-to-many fields like 'roles'

    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'roles', 'department')
        }),
        ('Work Conditions', {
            'fields': ('max_hours_per_week', 'can_work_extra', 'rotate_weekends', 'avoid_holidays', 'can_work_any_time', 'available_start_time', 'available_end_time'),
        }),
        ('Absences', {
            'fields': ('total_annual_leave', 'used_annual_leave', 'sick_days', 'unauthorized_absences', 'on_holiday', 'on_sick_leave'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.can_work_any_time:  # If they can work anytime, clear the available time
            obj.available_start_time = None
            obj.available_end_time = None
        super().save_model(request, obj, form, change)
        
@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    search_fields = ('name',)
    ordering = ('date',)

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('department', 'day_of_week', 'start_time', 'end_time', 'employee', 'is_sick')
    list_filter = ('department', 'day_of_week', 'is_sick')
    search_fields = ('employee__first_name', 'employee__last_name')
    ordering = ('day_of_week', 'start_time')

    actions = ['generate_shifts_action']

    def generate_shifts_action(self, request, queryset):
        generate_shifts()  # Poziva funkciju generiranja smjena
        self.message_user(request, "Smjene su uspješno generirane!")  # Notifikacija
        return HttpResponse("Smjene su generirane.", content_type="text/plain")
    
    generate_shifts_action.short_description = "Generiraj smjene za sve zahtjeve"

@admin.register(ShiftRequirement)
class ShiftRequirementAdmin(admin.ModelAdmin):
    list_display = ('department', 'role', 'day_of_week', 'shift_start_time', 'shift_end_time', 'required_employees')
    list_filter = ('department', 'role', 'day_of_week')
    search_fields = ('department__name', 'role__name')
    ordering = ('day_of_week', 'shift_start_time')

    actions = ['generate_schedule_action']

    def generate_schedule_action(self, request, queryset):
        generate_shifts()
        messages.success(request, "Raspored je uspješno generiran!")
        return redirect("/admin/schedule/shiftrequirement/")

    generate_schedule_action.short_description = "Generiraj raspored"

    class ShiftRequirementForm(forms.ModelForm):
        shift_start_time = forms.TimeField(
            widget=forms.TimeInput(attrs={'type': 'time'})
        )
        shift_end_time = forms.TimeField(
            widget=forms.TimeInput(attrs={'type': 'time'})
        )

        class Meta:
            model = ShiftRequirement
            fields = '__all__'

    form = ShiftRequirementForm

@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'hours_worked')
    list_filter = ('status', 'date', DateRangeFilter)
    search_fields = ('employee__first_name', 'employee__last_name')
    ordering = ('-date',)

    def changelist_view(self, request, extra_context=None):
        if 'date_range' in request.GET and request.GET['date_range'] == 'custom':
            form = CustomDateRangeForm(request.GET)
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                queryset = AttendanceReport.objects.filter(date__range=[start_date, end_date])
                extra_context = {'queryset': queryset}
            else:
                extra_context = {'form': form}
        return super().changelist_view(request, extra_context=extra_context)

# URL za generiranje rasporeda iz admin panela
def generate_schedule_view(request):
    generate_shifts()
    messages.success(request, "Raspored generiran!")
    return redirect("/admin/schedule/shiftrequirement/")

urlpatterns = [
    path("generate_schedule/", generate_schedule_view, name="generate_schedule_view"),
]
