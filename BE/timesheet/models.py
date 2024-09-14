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

class TimesheetTask(models.Model):
    TimeSheetID = models.ForeignKey(TimeSheet, on_delete=models.CASCADE, related_name='tasks')
    WorkPlan = models.TextField()
    IsComplete = models.BooleanField(default=False)
    Date= models.DateField()
    # # Tú Anh viết
    # def getTimeIn(self):
    #     current_time = self.TimeIn
    #     if current_time.hour < 8 or (current_time.hour == 8 and current_time.minute < 15):
    #         current_time = current_time.replace(hour=8, minute=0, second=0)
    #     if current_time.hour >= 12 and (current_time.hour < 14):
    #         current_time = current_time.replace(hour=14, minute=0, second=0)
    #     # if current_time.hour >= 12 and (current_time.hour < 13 or (current_time.hour == 13 and current_time.minute < 45)):
    #     #     current_time = current_time.replace(hour=13, minute=30, second=0)
    #     return current_time
    

    
    # def getTimeOut(self):
    #     checkout_time = self.TimeOut
    #     if checkout_time.hour > 17 or (checkout_time.hour == 17 and checkout_time.minute > 29):
    #         checkout_time = checkout_time.replace(hour=17, minute=30, second=0)
    #     if checkout_time.hour >= 12 and (checkout_time.hour < 14 ):
    #         checkout_time = checkout_time.replace(hour=12, minute=00, second=0)
    #     return checkout_time

    # def save(self, *args, **kwargs):
    #     if self.TimeIn and self.TimeOut:
    #         timein = self.getTimeIn()
    #         timeout = self.getTimeOut()
    #         print(timein,timeout)
    #         if timein.time() < time(12, 0) and timeout.time() > time(14,0):
    #             work_hours =(timeout - timein).total_seconds() / 3600- 2 
    #         else:
    #             work_hours =(timeout - timein).total_seconds() / 3600
           
    #         self.WorkHour = round(work_hours, 2)

    #     else:
    #         self.WorkHour = 0

    #     super(TimeSheet, self).save(*args, **kwargs)
