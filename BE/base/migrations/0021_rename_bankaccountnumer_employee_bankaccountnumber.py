# Generated by Django 4.2.7 on 2024-03-01 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0020_alter_employee_empstatus'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='BankAccountNumer',
            new_name='BankAccountNumber',
        ),
    ]
