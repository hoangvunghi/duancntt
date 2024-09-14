from rest_framework import serializers
from base.models import Employee
from .models import TimeSheet, TimesheetTask

class TimeSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSheet
        fields = "__all__"
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'work_hours' in self.context:
            data['WorkHour'] = self.context['work_hours']
        return data
        
class UserAccountWithTimeSheetSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Employee
        fields = "__all__"
        
class TimeSheetWithUserAccountSerializer(serializers.ModelSerializer):
    employee_id = UserAccountWithTimeSheetSerializer(source="employee", read_only=True)
    class Meta:
        model = TimeSheet
        fields = "__all__"

class TimesheetTaskSerializer(serializers.ModelSerializer):
    TimeSheetID = TimeSheetSerializer(read_only=True)
    class Meta:
        model = TimesheetTask
        fields = "__all__"

