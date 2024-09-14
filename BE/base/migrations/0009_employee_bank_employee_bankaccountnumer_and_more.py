# Generated by Django 4.2.7 on 2024-01-03 09:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('role', '0001_initial'),
        ('base', '0008_alter_useraccount_empid'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='Bank',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='BankAccountNumer',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='BankBranch',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='Gender',
            field=models.CharField(default=1, max_length=12),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='RoleID',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='role.role'),
        ),
        migrations.AddField(
            model_name='employee',
            name='TaxCode',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
