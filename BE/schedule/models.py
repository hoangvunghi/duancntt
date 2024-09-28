from django.db import models
# Create your models here.
from  base.models import Employee

class ConfigSchedule(models.Model):
    TimeBlock=models.TimeField()
    DateMin=models.IntegerField(default=3)
    Using=models.BooleanField(default=False)
class WorkShift(models.Model):
    COEFFICIENT_CHOICES = (
        (1, '1'),
        (2, '2'),
    )
    WorkShiftName=models.CharField(max_length=50)
    StartTime=models.TimeField()
    EndTime=models.TimeField()
    Color=models.CharField(max_length=20,default="#ccc")
    Coefficient = models.PositiveSmallIntegerField(choices=COEFFICIENT_CHOICES)  

    def __str__(self):
        return self.WorkShiftName  
    
    class Meta:
        verbose_name = 'Ca làm việc'
        verbose_name_plural = 'Ca làm việc'
        ordering = ['WorkShiftName']
    
class Schedule(models.Model):
    EmpID=models.ForeignKey(Employee,on_delete=models.CASCADE)
    Date=models.DateField()
    WorkShift=models.ForeignKey(WorkShift,null=True,on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Lịch làm việc'
        verbose_name_plural = 'Lịch làm việc'
        ordering = ['EmpID']


