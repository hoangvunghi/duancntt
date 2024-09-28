from django.db import models
from base.models import Employee
from schedule.models import WorkShift
from datetime import time

class TimeSheet(models.Model):
    TimeIn = models.DateTimeField(null=True, blank=True)
    TimeOut = models.DateTimeField(null=True, blank=True)
    EmpID = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    Late = models.FloatField(default=0,null=True,blank=True)
    WorkHour = models.FloatField(default=0,null=True,blank=True)
    class Meta:
        verbose_name = 'Chấm công'
        verbose_name_plural = 'Chấm công'
        ordering = ['TimeIn']

class TimesheetTask(models.Model):
    TimeSheetID = models.ForeignKey(TimeSheet, on_delete=models.CASCADE, related_name='tasks')
    WorkPlan = models.TextField()
    IsComplete = models.BooleanField(default=False)
    Date= models.DateField()
    
    class Meta:
        verbose_name = 'Công việc trong ngày'
        verbose_name_plural = 'Công việc trong ngày'
        ordering = ['Date']
    