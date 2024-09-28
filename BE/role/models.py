from django.db import models

class Role(models.Model):
    RoleID=models.AutoField(primary_key=True)
    RoleName=models.CharField(max_length=200)

    def __str__(self):
        return self.RoleName
    
    class Meta:
        verbose_name = 'Vai trò'
        verbose_name_plural = 'Vai trò'
        ordering = ['RoleID']
    