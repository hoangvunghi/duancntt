from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render
from datetime import timedelta
from leave.models import LeaveRequest
from django import forms
import pandas as pd
from io import BytesIO
from collections import defaultdict
from schedule.models import Schedule
from datetime import datetime
import calendar
from timesheet.models import TimeSheet
from django.http import FileResponse
from .models import UserAccount
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
def export_leave_info_view(request):
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


class ScheduleForm(forms.Form):
    from_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    # EmpID = forms.CharField(max_length=100, required=False)
from base.models import Employee
def export_schedule_info_view(request):
    if request.method == 'GET':
        form = ScheduleForm(request.GET)
        if form.is_valid():
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            emp_id = form.cleaned_data.get('EmpID')

            if not from_date and not to_date:
                now = datetime.now()
                _, last_day = calendar.monthrange(now.year, now.month)
                from_date = datetime(now.year, now.month, 1).date()
                to_date = datetime(now.year, now.month, last_day).date()

            if emp_id:
                employee = Employee.objects.get(EmpID=emp_id)
                emp_id = employee.EmpID
                emp_name = employee.EmpName
                schedules = Schedule.objects.filter(EmpID=emp_id, Date__range=[from_date, to_date])
            else:
                schedules = Schedule.objects.filter(Date__range=[from_date, to_date])

            schedule_data = defaultdict(list)
            for schedule in schedules:
                user_account = UserAccount.objects.get(EmpID=schedule.EmpID)
                schedule_data[(schedule.EmpID.EmpID, schedule.EmpID.EmpName, user_account.UserID)].append({
                    'date': schedule.Date,
                    'ca': schedule.WorkShift.WorkShiftName
                })

            date_range = pd.date_range(start=from_date, end=to_date)
            date_columns = [date.strftime('%Y-%m-%d') for date in date_range]
            frames = []
            for key, values in schedule_data.items():
                employee_data = pd.DataFrame(columns=date_columns)
                for date in date_range:
                    date_str = date.strftime('%Y-%m-%d')
                    records = "; ".join([f"{value['ca']}" for value in values if value['date'].strftime('%Y-%m-%d') == date_str])
                    if records:
                        employee_data.at[0, date_str] = records
                employee_data.insert(0, 'Employee ID', key[0])
                employee_data.insert(1, 'Employee Name', key[1])
                employee_data.insert(2, 'UserID', key[2])
                frames.append(employee_data)

            df = pd.concat(frames, ignore_index=True)

            excel_file = BytesIO()
            df.to_excel(excel_file, index=False)
            excel_file.seek(0)

            response = HttpResponse(excel_file.read(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="schedule_info.xlsx"'
            return response
    else:
        form = ScheduleForm()
    return render(request, 'admin/export_schedule_info.html', {'form': form})

class TimesheetForm(forms.Form):
    from_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    # EmpID = forms.CharField(required=False)

def timesheet_info_view(request):
    if request.method == 'GET':
        form = TimesheetForm(request.GET)
        if form.is_valid():
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            
            if from_date and to_date:
                timesheets = TimeSheet.objects.filter(TimeIn__date__range=[from_date, to_date])
            else:
                timesheets = TimeSheet.objects.all()

            timesheet_data = defaultdict(list)
            for item in timesheets.values('EmpID', 'EmpID__EmpName', 'TimeIn', 'TimeOut').order_by('TimeIn'):
                user_account = UserAccount.objects.get(EmpID=item['EmpID'])
                timesheet_data[(item['EmpID'], item['EmpID__EmpName'], user_account.UserID)].append({
                    'date': item['TimeIn'].date(),
                    'checkin': (item['TimeIn'] + timedelta(hours=7)).strftime('%H:%M:%S'),
                    'checkout': (item['TimeOut'] + timedelta(hours=7)).strftime('%H:%M:%S') if item['TimeOut'] else '0'
                })
            date_range = pd.date_range(start=from_date, end=to_date)
            date_columns = [date.strftime('%Y-%m-%d') for date in date_range]
            frames = []
            for key, values in timesheet_data.items():
                employee_data = pd.DataFrame(columns=date_columns)
                for date in date_range:
                    date_str = date.strftime('%Y-%m-%d')
                    records = "; ".join([f"{value['checkin']} - {value['checkout']}" for value in values if value['date'].strftime('%Y-%m-%d') == date_str])
                    if records:
                        employee_data.at[0, date_str] = records
                employee_data.insert(0, 'UserID', key[2])
                employee_data.insert(1, 'Employee ID', key[0])
                employee_data.insert(2, 'Employee Name', key[1])
                frames.append(employee_data)

            df = pd.concat(frames, ignore_index=True)

            # Write the DataFrame to an Excel file
            excel_file = 'timesheet_info.xlsx'
            df.to_excel(excel_file, index=False)

            # Create a FileResponse
            response = FileResponse(open(excel_file, 'rb'), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=%s' % excel_file
            return response
    else:
        form = TimesheetForm()

    return render(request, 'admin/export_timesheet_info.html', {'form': form})