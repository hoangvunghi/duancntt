from django.http import HttpResponse
from django.shortcuts import render
from datetime import timedelta
from leave.models import LeaveRequest
from django import forms
import pandas as pd
from io import BytesIO
from base.models import UserAccount
class ExportForm(forms.Form):
    from_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required= True,
        label='Ngày bắt đầu',
        )
    to_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), 
                              required= True,
                              label='Ngày kết thúc',
                              )
# def export_leave_info_view(request):
#     if request.method == 'POST':
#         form = ExportForm(request.POST)
#         if form.is_valid():
#             from_date = form.cleaned_data['from_date']
#             to_date = form.cleaned_data['to_date']
#             leaves = LeaveRequest.objects.filter(LeaveStartDate__range=[from_date, to_date])

#             leave_data = []
#             for leave in leaves:
#                 user_account = UserAccount.objects.get(EmpID=leave.EmpID)
#                 leave_data.append({
#                     "UserID": user_account.UserID,
#                     'Employee ID': leave.EmpID,
#                     'LeaveStartDate': (leave.LeaveStartDate.replace(tzinfo=None) + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
#                     'LeaveEndDate': (leave.LeaveEndDate.replace(tzinfo=None) + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
#                     'Status': leave.LeaveStatus,
#                     'Duration': str(leave.Duration),
#                 })
#             leave_data.sort(key=lambda x: x['UserID'])
#             df = pd.DataFrame(leave_data)
#             excel_file = BytesIO()
#             df.to_excel(excel_file, index=False)
#             excel_file.seek(0)

#             response = HttpResponse(excel_file.read(), content_type='application/vnd.ms-excel')
#             response['Content-Disposition'] = 'attachment; filename="leave_info.xlsx"'
#             return response
#     else:
#         form = ExportForm()
#     return render(request, 'admin/export_leave_info.html', {'form': form})

def export_leave_info(request):
    if request.method == 'POST':
        form = ExportForm(request.POST)
        if form.is_valid():
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            leaves = LeaveRequest.objects.filter(LeaveStartDate__range=[from_date, to_date])

            leave_data = []
            for leave in leaves:
                user_account = UserAccount.objects.get(EmpID=leave.EmpID)
                leave_data.append({
                    "UserID": user_account.UserID,
                    'Employee ID': leave.EmpID,
                    'LeaveStartDate': (leave.LeaveStartDate.replace(tzinfo=None) + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
                    'LeaveEndDate': (leave.LeaveEndDate.replace(tzinfo=None) + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
                    'Status': leave.LeaveStatus,
                    'Duration': str(leave.Duration),
                })
            leave_data.sort(key=lambda x: x['UserID'])
            df = pd.DataFrame(leave_data)
            excel_file = BytesIO()
            df.to_excel(excel_file, index=False)
            excel_file.seek(0)

            response = HttpResponse(excel_file.read(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="leave_info.xlsx"'
            return response
    else:
        form = ExportForm()
    return render(request, 'admin/export_leave_info.html', {'form': form})