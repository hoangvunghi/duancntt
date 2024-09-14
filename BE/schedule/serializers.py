from rest_framework import serializers
from .models import WorkShift, ConfigSchedule,Schedule
from base.serializers import EmployeeSerializer
class WorkShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkShift
        fields = '__all__'
        
        
class ConfigScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigSchedule
        fields = '__all__'
        
class ScheduleSerializer(serializers.ModelSerializer):
    WorkShiftDetail=WorkShiftSerializer(source='WorkShift', read_only=True)
    class Meta:
        model = Schedule
        fields = '__all__'
    
class ScheduleListSerializer(serializers.ModelSerializer):
    WorkShiftDetail=WorkShiftSerializer(source='WorkShift', read_only=True)
    EmployeeName=serializers.CharField(source='EmpID.EmpName', read_only=True)
    PhotoPath = serializers.SerializerMethodField()

    
    DepName=serializers.CharField(source='EmpID.DepID.DepName', read_only=True)
    Email=serializers.CharField(source='EmpID.Email', read_only=True)
    class Meta:
        model = Schedule
        fields = '__all__'
    def get_PhotoPath(self, obj):
        photo_path = obj.EmpID.PhotoPath  # Đường dẫn gốc từ mô hình
        return f'/media/{photo_path}'