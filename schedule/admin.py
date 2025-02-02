from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django import forms
from datetime import datetime, timedelta

from .models import Employee, Department, Role, Holiday, Shift, AttendanceReport, ShiftRequirement, WorkDay, FlexibleShift
from .generate_schedule import generate_shifts

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

class FlexibleShiftInline(admin.TabularInline):
    model = FlexibleShift
    extra = 1

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'work_start_time', 'work_end_time')
    search_fields = ('name',)
    inlines = [FlexibleShiftInline]

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'max_hours_per_week', 'total_assigned_hours', 'can_work_extra', 'on_holiday', 'on_sick_leave')
    list_filter = ('roles', 'department', 'can_work_extra', 'on_holiday', 'on_sick_leave')
    search_fields = ('first_name', 'last_name')
    ordering = ('last_name',)
    filter_horizontal = ('roles', 'available_days')

    def total_assigned_hours(self, obj):
        total_hours = Shift.objects.filter(employee=obj).aggregate(total_hours=admin.models.Sum('hours'))['total_hours'] or 0
        return total_hours
    total_assigned_hours.short_description = "Total Assigned Hours"

@admin.register(ShiftRequirement)
class ShiftRequirementAdmin(admin.ModelAdmin):
    list_display = ('department', 'role', 'day_of_week', 'shift_type', 'total_hours_needed', 'night_shift_hours_needed')
    list_filter = ('department', 'role', 'day_of_week')
    search_fields = ('department__name', 'role__name')
    ordering = ('day_of_week',)

    actions = ['generate_schedule_action']

    def generate_schedule_action(self, request, queryset):
        generate_shifts(request)
        messages.success(request, "Raspored je uspješno generiran za sve odjele!")
        return redirect("/admin/schedule/shiftrequirement/")

    generate_schedule_action.short_description = "Generiraj raspored za sve odjele"

@admin.register(WorkDay)
class WorkDayAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    search_fields = ('name',)
    ordering = ('date',)

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('department', 'day_of_week', 'start_time', 'end_time', 'employee', 'shift_hours')
    list_filter = ('department', 'day_of_week')
    search_fields = ('employee__first_name', 'employee__last_name')
    ordering = ('day_of_week', 'start_time')

    actions = ['generate_shifts_action']

    def generate_shifts_action(self, request, queryset):
        generate_shifts(request)
        messages.success(request, "Smjene su uspješno generirane!")
        return HttpResponse("Smjene su generirane.", content_type="text/plain")

    generate_shifts_action.short_description = "Generiraj smjene za sve zahtjeve"

    def shift_hours(self, obj):
        return obj.hours
    shift_hours.short_description = "Hours"
