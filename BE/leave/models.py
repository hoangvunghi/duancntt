from django.db import models
from base.models import Employee
from datetime import datetime
from leave_type.models import LeaveType
from datetime import time
# Create your models here.
class LeaveRequest(models.Model):
    LeaveRequestID = models.AutoField(primary_key=True, verbose_name='ID')
    EmpID = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Nhân viên')
    LeaveStartDate = models.DateTimeField(verbose_name='Ngày bắt đầu')
    LeaveEndDate = models.DateTimeField(verbose_name='Ngày kết thúc')
    # LeaveStartHour = models.TimeField(default=time(8, 0))
    # LeaveEndHour = models.TimeField(default=time(17, 30))
    LeaveTypeID = models.ForeignKey(LeaveType, on_delete=models.CASCADE, verbose_name='Loại nghỉ phép')
    Reason = models.CharField(max_length=500, verbose_name='Lý do')
    STATUS_CHOICES = [
        ('Chờ xác nhận', 'Chờ xác nhận'),
        ('Chờ phê duyệt', 'Chờ phê duyệt'),
        ('Đã phê duyệt', 'Đã phê duyệt'),
        ('Đã từ chối', 'Đã từ chối'),
    ]

    LeaveStatus = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default='Chờ xác nhận',
        verbose_name='Trạng thái'
    )
    Duration=models.IntegerField(null=True,blank=True, verbose_name='Số ngày nghỉ')
    
    def save(self, *args, **kwargs):
        if self.LeaveStartDate and self.LeaveEndDate:
            start_date = self.LeaveStartDate
            end_date = self.LeaveEndDate
            
            self.Duration = (end_date - start_date).days + 1
        else:
            self.Duration = 0
        
        super(LeaveRequest, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Đơn xin nghỉ phép'
        verbose_name_plural = 'Đơn xin nghỉ phép'
        ordering = ['LeaveRequestID']

from leave_type.models import LeaveType
class LeaveType(LeaveType):
    class Meta:
        proxy = True
        verbose_name = 'Loại nghỉ phép'
        verbose_name_plural = 'Loại nghỉ phép'

class LeaveExport(models.Model):
    class Meta:
        verbose_name = 'Xuất thông tin nghỉ phép'
        verbose_name_plural = 'Xuất thông tin nghỉ phép'
        
