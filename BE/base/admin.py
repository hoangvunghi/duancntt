from django.contrib import admin
from django.http import HttpResponse
from django.conf import settings
from timesheet.models import TimeSheet,TimesheetTask
from leave.models import LeaveRequest
from leave_type.models import LeaveType
from department.models import Department
from job.models import Job
from role.models import Role
from schedule.models import Schedule,WorkShift
from .models import Employee,UserAccount
from rest_framework.authtoken.models import Token
from .export import export_leave_info_view,export_schedule_info_view,timesheet_info_view
from django.urls import path
from django.http import FileResponse
from datetime import datetime, timedelta
import calendar
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

# Custom actions
def not_allow_edit(modeladmin, request, queryset):
    settings.ALLOW_EDIT_BY_ADMIN_ONLY = True
    return HttpResponse("Chỉnh sửa không được phép.")

import pandas as pd


def export_employee(modeladmin, request, queryset):
    data = []
    for employee in queryset:
        user_account = UserAccount.objects.get(EmpID=employee.EmpID)
        data.append({
            "UserID": user_account.UserID,
            "EmpID": employee.EmpID,
            "EmpName": employee.EmpName,
            "Email": employee.Email,
            'Role':employee.RoleID.RoleName,
            'Department':employee.DepID.DepName,
            "BankAccountNumber": employee.BankAccountNumber,
            "BankName": employee.BankName,
            "Gender": employee.Gender,
            "EmpStatus": employee.EmpStatus
        })
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="employees.xlsx"'
    df.to_excel(response, index=False)
    return response
export_employee.short_description = "Export to Excel"


def export_to_txt(modeladmin, request, queryset):
    content = "\n".join([f"{field}: {getattr(obj, field)}" for obj in queryset for field in obj.__dict__])
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=exported_data.txt'
    return response


# Custom action descriptions
not_allow_edit.short_description = "Not Allow Edit"
# export_to_txt.short_description = "Export selected objects to txt"

# Admin classes
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ["EmpID", "Date", "WorkShift"]
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('export_schedule_info/', self.admin_site.admin_view(export_schedule_info_view), name='export_schedule_info'),
        ]
        return my_urls + urls
    def export_schedule_info(self, request,_):
        return HttpResponseRedirect(reverse('admin:export_schedule_info'))
    actions = [export_schedule_info]

class UserAccountAdmin(admin.ModelAdmin):
    list_display = ["UserID", "EmpID"]

class TimeSheetInline(admin.TabularInline):
    model = TimeSheet

class EmployeeAdmin(admin.ModelAdmin):
    inlines = [TimeSheetInline]
    list_display = ["EmpID", "EmpName", "get_dep_name"]
    raw_id_fields = ["DepID", "JobID", "RoleID"]
    actions = [not_allow_edit, export_employee]

    def get_actions(self, request):
        actions = super().get_actions(request)
        return actions

    def get_list_editable(self, request):
        if settings.ALLOW_EDIT_BY_ADMIN_ONLY and not request.user.is_superuser:
            return None
        return super().get_list_editable(request)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if settings.ALLOW_EDIT_BY_ADMIN_ONLY and not request.user.is_superuser:
            return readonly_fields + [field.name for field in self.model._meta.fields]
        return readonly_fields

    def get_dep_name(self, obj):
        return obj.DepID.DepName if obj.DepID else ''

    get_dep_name.short_description = 'Department Name'

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["DepID", "DepName", "ManageID"]

class JobAdmin(admin.ModelAdmin):
    list_display = ["JobID", "JobName"]
    raw_id_fields = ["DepID"]

class TimeAdmin(admin.ModelAdmin):
    list_display = ["get_name", "TimeIn", "TimeOut"]
    raw_id_fields = ["EmpID"]
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('export_timesheet_info/', self.admin_site.admin_view(timesheet_info_view), name='export_timesheet_info'),
        ]
        return my_urls + urls
    def export_timesheet_info(self, request, _):
        return HttpResponseRedirect(reverse('admin:export_timesheet_info'))
    # actions = [export_to_txt]
    actions=[export_timesheet_info]

    def get_name(self, obj):
        return obj.EmpID.EmpName if obj.EmpID else ''

    get_name.short_description = "Employee Name"

# Register models with admin classes
admin.site.register(Role)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(TimeSheet, TimeAdmin)
admin.site.register(WorkShift)
admin.site.register(TimesheetTask)
