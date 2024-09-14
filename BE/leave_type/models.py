from django.db import models

# Create your models here.
class LeaveType(models.Model):
    LeaveTypeID = models.AutoField(primary_key=True, verbose_name='ID')
    LeaveTypeName = models.CharField(max_length=255, verbose_name='Loại nghỉ phép')
    # Subsidize=models.FloatField()
    LeaveTypeDescription=models.CharField(max_length=1000, verbose_name='Mô tả')
    LimitedDuration=models.IntegerField(verbose_name='Số ngày nghỉ tối đa')
    
    def __str__(self):
        return self.LeaveTypeName
    
    class Meta:
        verbose_name = 'Loại nghỉ phép'
        verbose_name_plural = 'Loại nghỉ phép'
        ordering = ['LeaveTypeID']