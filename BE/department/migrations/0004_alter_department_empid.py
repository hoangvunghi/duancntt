# Generated by Django 4.2.7 on 2023-12-19 03:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_alter_employee_depid_alter_employee_jobid'),
        ('department', '0003_alter_department_empid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='EmpID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.employee'),
        ),
    ]
