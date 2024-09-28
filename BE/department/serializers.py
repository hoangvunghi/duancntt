from base.models import Employee
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Department

class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()
    class Meta:
        model = Department
        fields = ['employee_count','DepID','DepName',"DepShortName",'ManageID']
    def get_employee_count(self, department):
        return Employee.objects.filter(DepID=department).count()


