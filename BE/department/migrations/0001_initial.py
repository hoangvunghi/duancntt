# Generated by Django 4.2.7 on 2023-12-16 05:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('DepID', models.IntegerField(primary_key=True, serialize=False)),
                ('DepName', models.CharField(max_length=255)),
                ('EmpID', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.employee')),
            ],
        ),
    ]
