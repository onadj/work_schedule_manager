from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Employee, Department

class EmployeeListView(ListView):
    model = Employee
    template_name = 'schedule/employee_list.html'

class EmployeeDetailView(DetailView):
    model = Employee
    template_name = 'schedule/employee_detail.html'

class DepartmentListView(ListView):
    model = Department
    template_name = 'schedule/department_list.html'

class DepartmentDetailView(DetailView):
    model = Department
    template_name = 'schedule/department_detail.html'
