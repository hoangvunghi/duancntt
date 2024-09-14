from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from base.models import Employee,UserAccount
from .models import TimeSheet,TimesheetTask
from .serializers import TimeSheetWithUserAccountSerializer, UserAccountWithTimeSheetSerializer,TimeSheetSerializer,TimesheetTaskSerializer
from base.permissions import IsAdminOrReadOnly,IsOwnerOrReadonly,IsHrAdminManager,IsHrAdmin
from rest_framework import permissions
from django.core.paginator import Paginator,EmptyPage
from django.utils import timezone
from datetime import timedelta,datetime
from schedule.models import Schedule,WorkShift
from department.models import Department
from role.models import Role
from job.models import Job
from collections import defaultdict
import math
from leave.models import LeaveRequest
from django.db.models import Sum, F, Value as V
from django.db.models.functions import Coalesce
import hashlib
from rest_framework.views import APIView
from datetime import time

import hashlib

def hash_string(input_string):
    # Create a hash object using SHA256 algorithm
    sha256 = hashlib.sha256()

    # Encode the input string to bytes
    input_bytes = input_string.encode('utf-8')

    # Update the hash object with the input bytes
    sha256.update(input_bytes)

    # Get the hashed value in hexadecimal representation
    hashed_value = sha256.hexdigest()

    return hashed_value
class SetIPAddress(APIView):
    permission_classes=[IsHrAdmin]
    def post(self, request):
        # Lấy địa chỉ IP từ request
        ip = request.META.get("HTTP_X_FORWARDED_FOR").split(',')[0]
        # Đọc giá trị băm đã lưu từ tệp
        try:
            with open("hash_key.txt", "r") as file:
                saved_hashed_ip = file.read()
        except FileNotFoundError:
            saved_hashed_ip = None
        # So sánh giá trị băm mới với giá trị băm đã lưu
        if hash_string(ip) == saved_hashed_ip:
            return Response({'message': 'Địa chỉ IP không đổi'}, status=status.HTTP_400_BAD_REQUEST)

        # Nếu giá trị băm mới khác với giá trị băm đã lưu, lưu giá trị mới vào tệp
        with open("hash_key.txt", "w") as file:
            file.write(hash_string(ip))

        return Response({'message': 'Địa chỉ IP đã được lưu mới'}, status=status.HTTP_201_CREATED)
@api_view(["GET"])
@permission_classes([IsHrAdmin])
def list_timesheet(request):
    page_index = request.GET.get('pageIndex', 1) 
    page_size = request.GET.get('pageSize', 10) 
    # total_attendance = TimeSheet.objects.count()
    order_by = request.GET.get('sort-by', 'id')
    asc = request.GET.get('asc', 'true').lower() == 'true'  
    try:
        page_size = int(page_size)
    except ValueError:
        return Response({"error": "Invalid value for items_per_page. Must be an integer.",
                        "status": status.HTTP_400_BAD_REQUEST},
                        status=status.HTTP_400_BAD_REQUEST)
    allowed_values = [10, 20, 30, 40, 50]
    if page_size not in allowed_values:
        return Response({"error": f"Invalid value for items_per_page. Allowed values are: {', '.join(map(str, allowed_values))}.",
                        "status": status.HTTP_400_BAD_REQUEST},
                        status=status.HTTP_400_BAD_REQUEST)
    if search_query := request.GET.get('query', ''):
        try:
            em_name = str(search_query)
            users = Employee.objects.filter(EmpName__icontains=em_name)
            time = TimeSheet.objects.filter(EmpID__in=users)
        except ValueError:
            return Response({"error": "Invalid value for name.",
                            "status": status.HTTP_400_BAD_REQUEST},
                            status=status.HTTP_400_BAD_REQUEST)
    else:
        time = TimeSheet.objects.all()

    from_date_str = request.GET.get('from')
    to_date_str = request.GET.get('to')
    if from_date_str and to_date_str:
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
            time = time.filter(TimeIn__date__range=[from_date, to_date])
        except ValueError:
            return Response({"error": "Invalid date format. Date format should be: YYYY-MM-DD.",
                            "status": status.HTTP_400_BAD_REQUEST},
                            status=status.HTTP_400_BAD_REQUEST)

    order_by = f"{'' if asc else '-'}{order_by}"
    time = time.order_by(order_by)
    total_attendance=time.count()
    paginator = Paginator(time, page_size)
    try:
        current_page_data = paginator.page(page_index)
    except EmptyPage:
        return Response({"error": "Page not found",
                        "status": status.HTTP_404_NOT_FOUND},
                        status=status.HTTP_404_NOT_FOUND)
    serialized_data = []
    for attendance_instance in current_page_data.object_list:
        user_account_data = UserAccountWithTimeSheetSerializer(attendance_instance.EmpID).data
        attendance_data = TimeSheetWithUserAccountSerializer(attendance_instance).data
        userid=UserAccount.objects.get(EmpID=user_account_data['EmpID']).UserID
        depname=Department.objects.get(DepID=user_account_data['DepID']).DepName
        rolename=Role.objects.get(RoleID=user_account_data['RoleID']).RoleName
        jobname=Job.objects.get(JobID=user_account_data['JobID']).JobName
        tasks = TimesheetTask.objects.filter(TimeSheetID=attendance_instance)
        tasks_data = TimesheetTaskSerializer(tasks, many=True).data
        for task in tasks_data:
            task.pop('TimeSheetID', None)
        combined_data = {**user_account_data, **attendance_data,"UserID":userid,"DepName":depname,"RoleName":rolename,"JobName":jobname,"Tasks": tasks_data}
        serialized_data.append(combined_data)
    return Response({
        "total_rows": total_attendance,
        "current_page": int(page_index),
        "data": serialized_data,
        "status": status.HTTP_200_OK
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsOwnerOrReadonly])
def list_timesheet_nv(request):
    page_index = request.GET.get('pageIndex', 1)
    page_size = request.GET.get('pageSize', 10)
    order_by = request.GET.get('sort_by', 'id')
    asc = request.GET.get('asc', 'true').lower() == 'true'
    order_by = f"{'' if asc else '-'}{order_by}"
    try:
        page_size = int(page_size)
    except ValueError:
        return Response({"error": "Invalid value for items_per_page. Must be an integer.",
                         "status": status.HTTP_400_BAD_REQUEST},
                        status=status.HTTP_400_BAD_REQUEST)
    allowed_values = [10, 20, 30, 40, 50]
    if page_size not in allowed_values:
        return Response({"error": f"Invalid value for items_per_page. Allowed values are: {', '.join(map(str, allowed_values))}.",
                         "status": status.HTTP_400_BAD_REQUEST},
                        status=status.HTTP_400_BAD_REQUEST)
    current_employee = request.user.EmpID.EmpID
    time = TimeSheet.objects.filter(EmpID=current_employee)

    from_date_str = request.GET.get('from')
    to_date_str = request.GET.get('to')
    if from_date_str and to_date_str:
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
            time = time.filter(TimeIn__date__range=[from_date, to_date])
        except ValueError:
            return Response({"error": "Invalid date format. Date format should be: YYYY-MM-DD.",
                            "status": status.HTTP_400_BAD_REQUEST},
                            status=status.HTTP_400_BAD_REQUEST)
    
    time = time.order_by(order_by)
    paginator = Paginator(time, page_size)
    current_employee_a = getattr(request.user, 'EmpID', None)
    try:
        current_page_data = paginator.page(page_index)
    except EmptyPage:
        return Response({"error": "Page not found",
                         "status": status.HTTP_404_NOT_FOUND},
                        status=status.HTTP_404_NOT_FOUND)
    serialized_data = []
    for attendance_instance in current_page_data.object_list:
        user_account_data = UserAccountWithTimeSheetSerializer(attendance_instance.EmpID).data
        attendance_data = TimeSheetWithUserAccountSerializer(attendance_instance).data
        tasks = TimesheetTask.objects.filter(TimeSheetID=attendance_instance)
        tasks_data = TimesheetTaskSerializer(tasks, many=True).data
        for task in tasks_data:
            task.pop('TimeSheetID', None)
        combined_data = {"EmpID":current_employee_a.EmpID,"EmpName":current_employee_a.EmpName, **attendance_data, "Tasks": tasks_data}
        serialized_data.append(combined_data)

    return Response({
        "total_rows": time.count(),
        "current_page": int(page_index),
        "data": serialized_data,
        "status": status.HTTP_200_OK
    }, status=status.HTTP_200_OK)


def get_existing_timesheet(emp_id, date):
    return TimeSheet.objects.filter(EmpID=emp_id, TimeIn__date=date).last()

def get_existing_timesheet_first(emp_id, date):
    return TimeSheet.objects.filter(EmpID=emp_id, TimeIn__date=date).first()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def check_in(request):
    try:
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    except AttributeError:
        return Response({"error": "No IP address found", "status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
    with open("hash_key.txt", "r") as file:
        hashed_value_old = file.read()
    print(client_ip)
    if hash_string(client_ip) == hashed_value_old:
        print("Hashes match: The values are identical.")
    else:
        print("Hashes do not match: The values are different.")
        return Response({"error": "Không ở công ty mà đòi check in",
                         "status": status.HTTP_404_NOT_FOUND},
                        status=status.HTTP_404_NOT_FOUND)
    emp_id = request.user.EmpID
    current_date = timezone.localtime(timezone.now()).date()  
    try:
        check = Schedule.objects.get(EmpID=emp_id, Date=current_date)
    except Schedule.DoesNotExist:
        return Response({"error": "You are not subscribed to your calendar today",
                         "status": status.HTTP_404_NOT_FOUND},
                        status=status.HTTP_404_NOT_FOUND)

    starttime = check.WorkShift.StartTime
    endtime = check.WorkShift.EndTime

    timenow = timezone.localtime(timezone.now())
    time1 = timenow.hour

    if time1 > endtime.hour:
        return Response({"message": "You did not sign up for this shift", "status": status.HTTP_404_NOT_FOUND},
                        status=status.HTTP_404_NOT_FOUND)
    if time1 < starttime.hour - 1:
        return Response({"message": "You did not sign up for this shift", "status": status.HTTP_404_NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND)
    
    existing_timesheet = get_existing_timesheet(emp_id, current_date)
    existing_timesheet_first = get_existing_timesheet_first(emp_id, current_date)
    timesheet= None
    if not existing_timesheet_first:
        if time1 > starttime.hour + 1 or (time1 == starttime.hour + 1 and timenow.minute >= starttime.minute):
            if time1>12 and starttime.hour<12:
                if time1<=2:
                    late_seconds=0
                else:
                    late_seconds = (time1 - 14 ) * 3600 + (timenow.minute - 0) * 60
            else:
                late_seconds = (time1 - starttime.hour ) * 3600 + (timenow.minute - starttime.minute) * 60
            late_hours = late_seconds / 3600

            # Tú Anh xóa dòng này
            # late = math.floor(late_hours)
            late= late_hours # Không làm tròn số

            current_time = timenow
            # Tú Anh xóa điều kiện checkin
            # if current_time.hour < 8 or (current_time.hour == 8 and current_time.minute < 15):
            #     current_time = current_time.replace(hour=8, minute=0, second=0)
            # if current_time.hour >= 12 and (current_time.hour < 14):
            #     current_time = current_time.replace(hour=14, minute=0, second=0)
            timesheet = TimeSheet.objects.create(EmpID=emp_id, TimeIn=current_time, Late=late)
            # serializer = TimeSheetSerializer(timesheet)
            # return Response({"message": "Checked in successfully", "data": serializer.data, "status": status.HTTP_200_OK},status=status.HTTP_200_OK)
    else:
        if existing_timesheet and not existing_timesheet.TimeOut:
            return Response({"error": "You have already checked in for today", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        
        current_time = timenow
        if current_time.hour >17 or (current_time.hour == 17 and current_time.minute >29):
            return Response({"message": "Cannot check in. Go home now.", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        # Tú Anh xóa điều kiện checkin
        # if current_time.hour < 8 or (current_time.hour == 8 and current_time.minute < 15):
        #     current_time = current_time.replace(hour=8, minute=0, second=0)
        # if current_time.hour >= 12 and (current_time.hour < 13 or (current_time.hour == 13 and current_time.minute < 45)):
        #     current_time = current_time.replace(hour=13, minute=30, second=0)
    
    current_time = timenow
    work_plans = request.data.get('work_plans',[])
    print(work_plans)
    if not work_plans or not isinstance(work_plans, list):
        pass
        # return Response({"error": "Work plans are required", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
    
    # Tu Anh sửa
    # Khong late
    if timesheet is None: 
        timesheet = TimeSheet.objects.create(EmpID=emp_id, TimeIn=current_time) 
    serializer = TimeSheetSerializer(timesheet)
    
    for work_plan in work_plans:
        TimesheetTask.objects.create(TimeSheetID=timesheet, WorkPlan=work_plan, Date=current_date)
    return Response({"message": "Checked in successfully", "data": serializer.data, 'work plans': work_plans, "status": status.HTTP_200_OK})
from datetime import datetime, time


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def check_out(request):
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    hash_ip = hash_string(client_ip)
    
    with open("hash_key.txt", "r") as file:
        hashed_value_old = file.read()
    
    if hash_ip != hashed_value_old:
        return Response({"error": "Không ở công ty mà đòi check out", "status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
    
    emp_id = request.user.EmpID
    current_date = timezone.now().date()
    existing_timesheet = get_existing_timesheet(emp_id, current_date)
    
    if not existing_timesheet or not existing_timesheet.TimeIn:
        return Response({"message": "Cannot check out. Not checked in today.", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
    if existing_timesheet.TimeOut:
        return Response({"message": "Cannot check out. Already checked out today.", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
    timein = existing_timesheet.TimeIn
    print(timein,"aaaaaa")
    if timein.hour < 1 or (timein.hour == 1 and timein.minute < 15):
        timein = timein.replace(hour=8, minute=0, second=0)
    
    if timein.hour >= 5 and timein.hour < 7:
        timein = timein.replace(hour=14, minute=0, second=0)
    
    checkout_time = timezone.localtime(timezone.now())
    
    if checkout_time < existing_timesheet.TimeIn:
        return Response({"message": "Cannot check out before check in time", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
    emp_id = request.user.EmpID
    current_date = timezone.localtime(timezone.now()).date()  
    try:
        check = Schedule.objects.get(EmpID=emp_id, Date=current_date)
    except Schedule.DoesNotExist:
        return Response({"error": "You are not subscribed to your calendar today",
                         "status": status.HTTP_404_NOT_FOUND},
                        status=status.HTTP_404_NOT_FOUND)
    
        
    starttime = check.WorkShift.StartTime
    starttimehour=starttime.hour
    starttimeminute=starttime.minute
    endtime = check.WorkShift.EndTime
    if timein.time() == time(14,0):
        timein = timein.replace(hour=starttimehour, minute=starttimeminute, second=0)
    if timein.hour <starttime.hour:
        if starttime.hour>12:
            timein = timein.replace(hour=starttimehour, minute=starttimeminute, second=0)
    existing_timesheet.TimeOut = checkout_time
    timeout = checkout_time 
    
    if timeout.hour > 17 or (timeout.hour == 17 and timeout.minute > 29):
        timeout = timeout.replace(hour=17, minute=30, second=0)
    
    if timeout.hour >= 12 and timeout.hour < 14:
        timeout = timeout.replace(hour=12, minute=0, second=0)
    if endtime.hour<=timeout.hour:
        if endtime.hour<=12:
            timeout = timeout.replace(hour=12, minute=0, second=0)
        if endtime.hour==17:
            timeout = timeout.replace(hour=17, minute=30, second=0)
    if timein.time() < time(12, 0) and timeout.time() > time(14, 0):
        work_hours = (timeout - timein).total_seconds() / 3600 - 2
    else:
        work_hours = (timeout - timein).total_seconds() / 3600
    if timein.hour==8 and timein.minute==0 and timein.second==0:
        existing_timesheet.WorkHour = round(work_hours, 2) +7
    elif timein.hour==14 and timein.minute==0 and timein.second==0:
        existing_timesheet.WorkHour = round(work_hours, 2) +7
    else:
        existing_timesheet.WorkHour = round(work_hours, 2) 
    
    task_updates = request.data.get('task_updates', '')
    if not task_updates:
        pass
    for task_update in task_updates:
        task_id = task_update.get('id')
        is_complete = task_update.get('is_complete')
        task = TimesheetTask.objects.filter(id=task_id, TimeSheetID=existing_timesheet).first()
        if task:
            task.IsComplete = is_complete
            task.save()

    new_tasks = request.data.get('new_tasks', '')
    if not new_tasks:
        pass
    else:
        for new_task in new_tasks:
            TimesheetTask.objects.create(TimeSheetID=existing_timesheet, WorkPlan=new_task, IsComplete=True,Date=current_date)
    if not TimesheetTask.objects.filter(TimeSheetID=existing_timesheet).exists():
        return Response({"error": "Cannot check out. No task today", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
    try:
        existing_timesheet.save() 
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)  
    serializer = TimeSheetSerializer(existing_timesheet)

    return Response({"message": "Checked out successfully", "data": serializer.data, "status": status.HTTP_200_OK})


@api_view(["GET"])
@permission_classes([IsAdminOrReadOnly])
def list_timesheet_raw(request):
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')

    if from_date and to_date:
        time = TimeSheet.objects.filter(TimeIn__date__range=[from_date, to_date])
    else:
        time = TimeSheet.objects.all()
    serialized_data= {}
    for attendance_instance in time:
        if attendance_instance.EmpID not in serialized_data:
            user_account_data = UserAccountWithTimeSheetSerializer(attendance_instance.EmpID).data

            userid = UserAccount.objects.get(EmpID=user_account_data['EmpID']).UserID
            depname = Department.objects.get(DepID=user_account_data['DepID']).DepName
            rolename = Role.objects.get(RoleID=user_account_data['RoleID']).RoleName
            jobname = Job.objects.get(JobID=user_account_data['JobID']).JobName

            serialized_data[attendance_instance.EmpID] = {
                **user_account_data,
                "UserID": userid,
                "DepName": depname,
                "RoleName": rolename,
                "JobName": jobname,
                "DateValue": defaultdict(lambda: {'total_late': 0, 'total_workhour': 0,'tasks': []}),

            }

            timesheets = TimeSheet.objects.filter(EmpID=attendance_instance.EmpID)
            for timesheet in timesheets:
                timesheet_data = TimeSheetWithUserAccountSerializer(timesheet).data
                date_str = timesheet.TimeIn.strftime("%Y-%m-%d")

                serialized_data[attendance_instance.EmpID]["DateValue"][date_str]['total_late'] += timesheet_data.get('Late', 0)
                serialized_data[attendance_instance.EmpID]["DateValue"][date_str]['total_workhour'] += timesheet_data.get('WorkHour', 0)
                tasks = TimesheetTask.objects.filter(TimeSheetID=timesheet)
                task_data = TimesheetTaskSerializer(tasks, many=True).data
                for task in task_data:
                    task.pop('Date', None)
                    task.pop('TimeSheetID', None)
                serialized_data[attendance_instance.EmpID]["DateValue"][date_str]['tasks'].extend(task_data)
            serialized_data[attendance_instance.EmpID]["DateValue"] = dict(sorted(serialized_data[attendance_instance.EmpID]["DateValue"].items()))

    serialized_data = list(serialized_data.values())

    return Response({
        "data": serialized_data,
        "status": status.HTTP_200_OK
    }, status=status.HTTP_200_OK)
from django.db.models import FloatField

@api_view(["GET"])
@permission_classes([IsHrAdminManager])
def list_registered_without_attendance(request):
    emp_name = request.GET.get('EmpName')  
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    serialized_data = []
    if emp_name:
        all_employee = Employee.objects.filter(EmpName__icontains=emp_name).values_list('EmpID', flat=True)
    else:
        all_employee = Employee.objects.values_list('EmpID', flat=True)
    all_employee = list(all_employee)
    for emp_id in all_employee:
        user_account_instance = Employee.objects.get(EmpID=emp_id)
        user_account_data = UserAccountWithTimeSheetSerializer(user_account_instance).data
        depname = ""
        rolename = ""
        jobname = ""
        userid = UserAccount.objects.get(EmpID=user_account_instance.EmpID).UserID
        if user_account_instance.DepID:
            depid = user_account_instance.DepID.DepID
            depname = Department.objects.get(DepID=depid).DepName
        
        if user_account_instance.RoleID:
            roleid = user_account_instance.RoleID.RoleID
            rolename = Role.objects.get(RoleID=roleid).RoleName
        
        if user_account_instance.JobID:
            jobid = user_account_instance.JobID.JobID
            jobname = Job.objects.get(JobID=jobid).JobName
        if from_date and to_date:
            schedules = Schedule.objects.filter(EmpID=emp_id, Date__range=[from_date, to_date]).values_list('Date', flat=True).distinct()
            leaverequest = LeaveRequest.objects.filter(EmpID=emp_id, LeaveStartDate__range=[from_date, to_date],LeaveStatus="Đã phê duyệt")
            attended = TimeSheet.objects.filter(TimeIn__date__range=[from_date, to_date]).values_list('TimeIn', flat=True).distinct()
            schedulescof2 = Schedule.objects.filter(EmpID=emp_id, Date__range=[from_date, to_date],WorkShift__Coefficient=2).values_list('Date', flat=True).distinct()
        else:
            today = datetime.today().date()
            yesterday = today - timedelta(days=1)
            leaverequest = LeaveRequest.objects.filter(EmpID=emp_id, LeaveStartDate__lte=yesterday,LeaveStatus="Đã phê duyệt")
            schedules = Schedule.objects.filter(EmpID=emp_id, Date__lte=yesterday).values_list('Date', flat=True).distinct()
            attended = TimeSheet.objects.filter(EmpID=emp_id, TimeIn__date__lte=yesterday).values_list('TimeIn', flat=True).distinct()
            schedulescof2 = Schedule.objects.filter(EmpID=emp_id, WorkShift__Coefficient=2, Date__lte=yesterday).values_list('Date', flat=True).distinct()
        
        attended = [time_in.strftime('%Y-%m-%d') for time_in in attended]
        total=0
        not_attended_dates = []
        
        leaverequest_dates = []
        for request in leaverequest:
            start_date = request.LeaveStartDate
            end_date = request.LeaveEndDate
            while start_date <= end_date:
                leaverequest_dates.append(start_date.strftime("%Y-%m-%d"))  
                start_date += timedelta(days=1) 
        
        for schedule in schedules:
            date_str = schedule.strftime("%Y-%m-%d")
            if date_str not in attended:
                workship = Schedule.objects.get(EmpID=emp_id, Date=date_str)
                work_shift = workship.WorkShift
                coe = work_shift.Coefficient
                print(total)
                if coe == 2:
                    total = 2
                else:
                    total = 1
                if date_str in leaverequest_dates:
                    pass
                else:
                    not_attended_dates.append({"date": date_str, "coe": total})
        
        for schedule in schedulescof2:
            date_str = schedule.strftime("%Y-%m-%d")
            if date_str not in [item["date"] for item in not_attended_dates]:
                total_workhour = TimeSheet.objects.filter(EmpID=emp_id, TimeIn__date=date_str).aggregate(total_workhour=Coalesce(Sum('WorkHour'), V(0), output_field=FloatField()))['total_workhour']
                if total_workhour is None:
                    total_workhour = 0
                if 0 < total_workhour < 4:
                    total = 1
                    not_attended_dates.append({"date": date_str, "coe": total})
        
        not_attended_dates.sort(key=lambda x: x['date'])
        combined_data = {
            **user_account_data,
            "UserID": userid,
            "DepName": depname,
            "RoleName": rolename,
            "JobName": jobname,
            "NotAttendedDates": not_attended_dates,
        }
        serialized_data.append(combined_data)

    return Response({
        "data": serialized_data,
        "status": status.HTTP_200_OK
    }, status=status.HTTP_200_OK)
    

from collections import defaultdict
from django.db.models import Min, Max
import pandas as pd
import calendar
from django.http import FileResponse
from rest_framework_simplejwt.tokens import AccessToken
@api_view(["GET"])
# @permission_classes([IsAdminOrReadOnly])
def timesheet_info(request):
    token = request.GET.get('token')
    if not token:
        return Response("You are not authorized to download this data.")
    token_obj = AccessToken(token)
    user_id = token_obj['user_id']
    user = UserAccount.objects.get(UserID=user_id)
    if user.is_system_admin(request) or user.is_hr_admin_manager(request):
        pass
    else:
        return Response("You are not authorized to download this data.")
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    emp_name = request.GET.get('EmpName')

    if from_date and to_date:
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')
        if emp_name:
            timesheets = TimeSheet.objects.filter(EmpID__EmpName=emp_name, TimeIn__date__range=[from_date, to_date])
        else:
            timesheets = TimeSheet.objects.filter(TimeIn__date__range=[from_date, to_date])
    else:
        if emp_name:
            timesheets = TimeSheet.objects.filter(EmpID__EmpName=emp_name)
        else:
            timesheets = TimeSheet.objects.all()
    now = datetime.now()
    if not from_date and not to_date:
        _, last_day = calendar.monthrange(now.year, now.month)
        from_date = datetime(now.year, now.month, 1)
        to_date = datetime(now.year, now.month, last_day)
    timesheet_data = defaultdict(list)
    for item in timesheets.values('EmpID__EmpName', 'TimeIn', 'TimeOut').order_by('TimeIn'):
        timesheet_data[item['EmpID__EmpName']].append({
            'date': item['TimeIn'].date(),
            'checkin': (item['TimeIn'] + timedelta(hours=7)).strftime('%H:%M:%S'),
            'checkout': (item['TimeOut'] + timedelta(hours=7)).strftime('%H:%M:%S') if item['TimeOut'] else '0'
        })
    
    # Create a DataFrame with columns for each day in the date range
    # date_range = pd.date_range(start=from_date, end=to_date)
    # columns = ['Employee'] + [date.strftime('%Y-%m-%d') for date in date_range]
    # df = pd.DataFrame(columns=columns)

    # # Fill in the DataFrame with the timesheet data
    # for key, values in timesheet_data.items():
    #     employee_data = {'employee': key}
    #     for value in values:
    #         date = value['date'].strftime('%Y-%m-%d')
    #         if date in df.columns:
    #             employee_data[date] = f"{value['first_checkin']} - {value['last_checkout']}"
    #     df = df.append(employee_data, ignore_index=True)

    # # Write the DataFrame to an Excel file
    # excel_file = 'timesheet_info.xlsx'
    # df.to_excel(excel_file, index=False)

    # # Create a FileResponse
    # response = FileResponse(open(excel_file, 'rb'), content_type='application/vnd.ms-excel')
    # response['Content-Disposition'] = 'attachment; filename=%s' % excel_file
    # return response
    
    date_range = pd.date_range(start=from_date, end=to_date)
    date_columns = [date.strftime('%Y-%m-%d') for date in date_range]
    frames = []
    max_rows = 0
    for key, values in timesheet_data.items():
        employee_data = pd.DataFrame(columns=date_columns)
        for date in date_range:
            date_str = date.strftime('%Y-%m-%d')
            records = "; ".join([f"{value['checkin']} - {value['checkout']}" for value in values if value['date'].strftime('%Y-%m-%d') == date_str])
            if records:
                max_rows = max(max_rows, len(records))
                employee_data.at[0, date_str] = records
        employee_data.insert(0, 'Employee', key)
        frames.append(employee_data)

    df = pd.concat(frames, ignore_index=True)

    # Write the DataFrame to an Excel file
    excel_file = 'timesheet_info.xlsx'
    df.to_excel(excel_file, index=False)

    # Create a FileResponse
    response = FileResponse(open(excel_file, 'rb'), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s' % excel_file
    return response


@api_view(['GET'])
@permission_classes([IsHrAdmin])
def list_timesheettask_manage(request):
    from_date = request.query_params.get('from', datetime.now().date())
    to_date = request.query_params.get('to', datetime.now().date())

    if isinstance(from_date, str):
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
    if isinstance(to_date, str):
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

    queryset = TimesheetTask.objects.filter(Date__range=[from_date, to_date])
    serializer = TimesheetTaskSerializer(queryset, many=True)
    

    grouped_tasks = {}
    for task in serializer.data:
        timesheet_data = task.pop('TimeSheetID', {})
        task_data = task
        emp_id = timesheet_data.get('EmpID')
        # emp_name = Employee.objects.get(EmpID=emp_id).EmpID
        timesheet_id = timesheet_data.get('id')
        if timesheet_id not in grouped_tasks:
            grouped_tasks[timesheet_id] = {
                "EmployeeID": emp_id,
                "TimeIn": timesheet_data.get('TimeIn'),
                "TimeOut": timesheet_data.get('TimeOut'),
                "Tasks": []
            }
        grouped_tasks[timesheet_id]["Tasks"].append(task_data)

    grouped_data = list(grouped_tasks.values())


    return Response({
        "data": grouped_data,
        "status": status.HTTP_200_OK,
        "message": "Successfully retrieved timesheet tasks."
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsOwnerOrReadonly])
def user_timesheet_tasks(request):
    emp_id = request.user.EmpID.EmpID
    # emp_name = request.user.EmpID.EmpName

    from_date = request.query_params.get('from', datetime.now().date())
    to_date = request.query_params.get('to', datetime.now().date())

    if isinstance(from_date, str):
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
    if isinstance(to_date, str):
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

    queryset = TimesheetTask.objects.filter(Date__range=[from_date, to_date], TimeSheetID__EmpID=emp_id)
    if not queryset.exists():
        timein=get_existing_timesheet(emp_id,datetime.now().date()).TimeIn
        return Response({
            "data": {
                "EmployeeID": emp_id,
                "data":[{
                    "TimeIn":timein,
                    "TimeOut":None,
                    "Tasks": []
                }]
            },
            "status": status.HTTP_200_OK,
            "message": "No timesheet tasks found."
        }, status=status.HTTP_200_OK)
    else:
        serializer = TimesheetTaskSerializer(queryset, many=True)
        grouped_tasks = {}
        for task in serializer.data:
            timesheet_data = task.pop('TimeSheetID', {})
            task_data = task
            timesheet_id = timesheet_data.get('id')
            if timesheet_id not in grouped_tasks:
                grouped_tasks[timesheet_id] = {
                    "TimeIn": timesheet_data.get('TimeIn'),
                    "TimeOut": timesheet_data.get('TimeOut'),
                    "Tasks": []
                }
            grouped_tasks[timesheet_id]["Tasks"].append(task_data)

        grouped_data = {
            "EmployeeID": emp_id,
            "data": list(grouped_tasks.values())
        }
        return Response({
            "data": grouped_data,
            "status": status.HTTP_200_OK,
            "message": "Successfully retrieved timesheet tasks."
        }, status=status.HTTP_200_OK)