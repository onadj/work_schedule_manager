from django.contrib import admin
from .models import Employee, Department, Role, Holiday, Shift, AttendanceReport
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django import forms
from datetime import datetime, timedelta

# Custom filter class for filtering by date range
class DateRangeFilter(SimpleListFilter):
    title = _('date range')  # or use a custom title
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
            # No default implementation for custom date filter here
            pass
        return queryset


# Form for custom date range
class CustomDateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.SelectDateWidget())
    end_date = forms.DateField(widget=forms.SelectDateWidget())


# Customize the admin view for AttendanceReport
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
    list_display = ('first_name', 'last_name', 'max_hours_per_week', 'can_work_extra', 'rotate_weekends')
    list_filter = ('roles', 'department', 'can_work_extra', 'rotate_weekends')
    search_fields = ('first_name', 'last_name')
    ordering = ('last_name',)

    filter_horizontal = ('roles', 'department')  # Enables multi-select in admin panel

    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'roles', 'department')
        }),
        ('Work Conditions', {
            'fields': ('max_hours_per_week', 'can_work_extra', 'rotate_weekends', 'avoid_holidays'),
        }),
        ('Absences', {
            'fields': ('total_annual_leave', 'used_annual_leave', 'sick_days', 'unauthorized_absences'),
        }),
    )

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

@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'hours_worked')
    list_filter = ('status', 'date', DateRangeFilter)  # Adding custom DateRangeFilter to the list_filter
    search_fields = ('employee__first_name', 'employee__last_name')
    ordering = ('-date',)

    # Override changelist_view to display custom date range form
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

    def get_search_results(self, request, queryset, search_term):
        # Ensure this method returns both a queryset and a flag indicating possible duplicates
        if 'start_date' in request.GET and 'end_date' in request.GET:
            start_date = request.GET['start_date']
            end_date = request.GET['end_date']
            return queryset.filter(date__gte=start_date, date__lte=end_date), False
        return queryset, False  # Default return for search functionality
