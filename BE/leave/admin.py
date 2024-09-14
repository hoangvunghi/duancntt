from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import LeaveRequest, LeaveType, LeaveExport

class LeaveAdmin(admin.ModelAdmin):
    change_list_template = 'admin/leave_change_list.html'
    list_display = ["get_name", "LeaveStatus", "LeaveTypeID", "LeaveStartDate", "LeaveEndDate", "Duration"]
    raw_id_fields = ["LeaveTypeID"]
    list_filter = ['EmpID', 'LeaveStartDate', 'LeaveEndDate', 'LeaveTypeID', 'LeaveStatus']
    search_fields = ['EmpID__EmpName', 'LeaveTypeID__LeaveTypeName', 'LeaveStatus']
    # def get_urls(self):
    #     urls = super().get_urls()
    #     my_urls = [
    #         path('export_leave_info/', self.admin_site.admin_view(export_leave_info_view), name='export_leave_info'),
    #     ]
    #     return my_urls + urls
    # def export_leave_info(self, request,_):
    #     return HttpResponseRedirect(reverse('admin:export_leave_info'))
    # actions = [export_leave_info]
    def get_name(self, obj):
        return obj.EmpID.EmpName if obj.EmpID else ''

    def save_model(self, request, obj, form, change):
        if obj.LeaveStartDate and obj.LeaveEndDate:
            duration = (obj.LeaveEndDate - obj.LeaveStartDate).days + 1
            obj.Duration = duration
        super().save_model(request, obj, form, change)

    get_name.short_description = 'Employee Name'

admin.site.register(LeaveRequest, LeaveAdmin)



class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ["LeaveTypeID", "LeaveTypeName", "LeaveTypeDescription", "LimitedDuration"]
    list_filter = ['LimitedDuration']
    search_fields = ['LeaveTypeName', 'LeaveTypeDescription', 'LimitedDuration']

admin.site.register(LeaveType, LeaveTypeAdmin)


from .export import ExportForm
class LeaveExportAdmin(admin.ModelAdmin):
    change_list_template = 'admin/leave_export_change_list.html'
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return True
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['form'] = ExportForm()
        return super().changelist_view(request, extra_context)
        

admin.site.register(LeaveExport, LeaveExportAdmin)