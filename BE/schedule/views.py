from datetime import datetime,timedelta
from django.http import Http404
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from base.permissions import IsAdminOrReadOnly,IsHrAdmin,IsAdmin
from .models import WorkShift, ConfigSchedule, Schedule
from rest_framework.pagination import PageNumberPagination
from .serializers import WorkShiftSerializer, ConfigScheduleSerializer, ScheduleSerializer,ScheduleListSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import  IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist

class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'pageSize'
    page_query_param = 'pageIndex'


class BaseAPIView(viewsets.ModelViewSet):
    pagination_class = CustomPageNumberPagination

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_by = self.request.query_params.get('sort_by', '-id')
        if (self.request.query_params.get('asc') == "true"):
            return queryset.order_by(sort_by)
        if (self.request.query_params.get('asc') == "false"):
            return queryset.order_by(f'-{sort_by}')
        return queryset

    @extend_schema(parameters=[
        OpenApiParameter(name='sort_by', type=str,
                         location='query', description='Field to sort by'),
        OpenApiParameter(name='asc', type=str, location='query',
                         description='Sort order (ascending/descending)')
    ])
    def list(self, request, *args, **kwargs):

        if 'pageSize' not in self.request.query_params and 'pageIndex' not in self.request.query_params:
            queryset = super().get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            response_data = {
                'total_rows': queryset.count(),
                'data': serializer.data
            }
            return Response(response_data)
        response = super().list(request, *args, **kwargs)

        response_data = {
            'total_rows': response.data['count'],
            'data': response.data['results']
        }
        return Response(response_data)


class WorkShiftAPIView(BaseAPIView):
    queryset = WorkShift.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = WorkShiftSerializer


class ConfigScheduleAPIView(BaseAPIView):
    queryset = ConfigSchedule.objects.all()
    permission_classes = [IsAdmin]
    serializer_class = ConfigScheduleSerializer

    def create(self, request, *args, **kwargs):
        using_config_schedule_exists = ConfigSchedule.objects.filter(
            Using=True).exists()
        if using_config_schedule_exists:
            return Response({"message": "Không thể tạo vì có 1 cấu hình đang được sử dụng"}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        using_config_schedule_exists = ConfigSchedule.objects.exclude(
            id=instance.id).filter(Using=True).exists()

        if using_config_schedule_exists and request.data.get('Using', instance.Using):
            return Response({"message": "Không thể sửa vì có 1 cấu hình đang được sử dụng"}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)


class ScheduleAPiView(BaseAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        type = self.request.query_params.get('type', 'reg')
        
        if user.is_hr_or_admin(self.request) and type=="list":
            queryset = queryset
        else:
            queryset = queryset.filter(EmpID_id=user.EmpID)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()  
        month = self.request.query_params.get('month')
        
        year = self.request.query_params.get('year')
        if month is not None and year is not None:
            try:
                date_min = datetime(int(year), int(month), 1)
                date_max = datetime(int(year), int(month) + 1, 1)
                queryset = queryset.filter(
                    Date__gte=date_min, Date__lt=date_max)
                serializer = self.get_serializer(queryset, many=True)
                response_data = {
                    'total_rows': queryset.count(),
                    'data': serializer.data
                }
                return Response(response_data)
            except ValueError:
                raise Http404("Invalid month or year")
        return super().list(request, *args, **kwargs)
    def create(self, request, *args, **kwargs):
            emp_id = request.data.get('EmpID')
            date = request.data.get('Date')
            work_shift_id = request.data.get('WorkShift')

            config_schedule = ConfigSchedule.objects.get(Using=True)
            lock_time = config_schedule.TimeBlock
            current_time = datetime.now()
            date = datetime.strptime(date, "%Y-%m-%d")
            next_sunday = current_time + timedelta(days=(6 - current_time.weekday()) )
            next_sunday_lock_time = datetime.combine(next_sunday.date(), lock_time)
            if date >= next_sunday_lock_time:
                try:
                    existing_record = Schedule.objects.get(Date=date, EmpID=emp_id)
                    existing_record.WorkShift = WorkShift.objects.get(id=work_shift_id)
                    existing_record.save()
                    serializer = self.get_serializer(existing_record)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except ObjectDoesNotExist:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Chỉ được đăng kí lịch sau tuần này."}, status=status.HTTP_400_BAD_REQUEST)

        

class ConfigScheduleUsingTrueAPIView(generics.ListAPIView):
    serializer_class = ConfigScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ConfigSchedule.objects.filter(Using=True)

@extend_schema(parameters=[
        OpenApiParameter(name='workshift', type=str,
                         location='query', description='Field to workshift'),
        OpenApiParameter(name='day', type=str, location='query',
                         description='filter by day')
    ])
class ScheduleListShiftAPIView(generics.ListAPIView):
    serializer_class = ScheduleListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        workshift = self.request.query_params.get('workshift')
        day = self.request.query_params.get('day')
        if workshift=="all":
            return Schedule.objects.filter(Date=day)
        return Schedule.objects.filter(WorkShift__WorkShiftName=workshift,Date=day)


from collections import defaultdict
from rest_framework.decorators import api_view, permission_classes
import pandas as pd
from django.http import FileResponse
from calendar import monthrange
import calendar
from rest_framework_simplejwt.tokens import AccessToken
from base.models import UserAccount
@api_view(["GET"])
# @permission_classes([IsAdminOrReadOnly])
def schedule_info(request): 
    token = request.GET.get('token')
    if not token:
        return Response("You are not authorized to download this data.")
    token_obj = AccessToken(token)
    user_id = token_obj['user_id']
    user = UserAccount.objects.get(UserID=user_id)
    if user.is_system_admin(request) or user.is_hr_admin_manager(request):
        pass
    else:
        return Response("You don't have permission to download this data.")
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    emp_id = request.GET.get('EmpID')

    now = datetime.now()
    if not from_date and not to_date:
        _, last_day = calendar.monthrange(now.year, now.month)
        from_date = datetime(now.year, now.month, 1).date()
        to_date = datetime(now.year, now.month, last_day).date()
    else:
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

    if emp_id:
        schedules = Schedule.objects.filter(EmpID=emp_id, Date__range=[from_date, to_date])
    else:
        schedules = Schedule.objects.filter(Date__range=[from_date, to_date])

    schedule_data = defaultdict(list)
    for schedule in schedules:
        schedule_data[schedule.EmpID].append({
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
        employee_data.insert(0, 'Employee', key)
        frames.append(employee_data)

    df = pd.concat(frames, ignore_index=True)

    excel_file = 'schedule_info.xlsx'
    df.to_excel(excel_file, index=False)

    # Create a FileResponse
    response = FileResponse(open(excel_file, 'rb'), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s' % excel_file
    return response