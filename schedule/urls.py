from django.urls import path
from .views import EmployeeListView, EmployeeDetailView, DepartmentListView, DepartmentDetailView

app_name = 'schedule'

urlpatterns = [
    path('employee/', EmployeeListView.as_view(), name='employee_list'),
    path('employee/<int:pk>/', EmployeeDetailView.as_view(), name='employee_detail'),
    path('department/', DepartmentListView.as_view(), name='department_list'),
    path('department/<int:pk>/', DepartmentDetailView.as_view(), name='department_detail'),
]
