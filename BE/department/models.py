from django.db import models

class Department(models.Model):
    # DepStatus=models.BooleanField(default=True)
    DepID = models.AutoField(primary_key=True)
    DepName = models.CharField(max_length=255)
    DepShortName=models.CharField(max_length=3)
    ManageID = models.ForeignKey('base.Employee',on_delete=models.SET_NULL,null=True,blank=True)

    class Meta:
        verbose_name = 'Phòng ban'
        verbose_name_plural = 'Phòng ban'
        ordering = ['DepID']