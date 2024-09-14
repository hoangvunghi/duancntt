# create_admin.py

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrmm.settings')
# Initialize Django
django.setup()


from base.models import UserAccount
from role.models import Role
admin = UserAccount.objects.create_superuser(
    UserID='admin',
    email='admin@gmail.com',
    name='admin',
    password='admin'
)
roles = ['Admin', 'Hr', 'Employee', 'Manager']
for role_name in roles:
    role, created = Role.objects.get_or_create(RoleName=role_name)
admin_role = Role.objects.get(RoleName='Admin')
admin_user = UserAccount.objects.get(UserID='admin')
admin_user.EmpID.RoleID = admin_role

# Save the admin user
admin_user.EmpID.save() 
