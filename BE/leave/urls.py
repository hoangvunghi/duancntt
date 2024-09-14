from django.urls import path
from leave import views
from .export import export_leave_info

urlpatterns=[
    path("leave/list-leave",views.list_leave,name="list-leave"),
    path('leave/create-leave', views.create_leave, name='create-leave'),
    path('leave/update-leave/<int:pk>', views.update_leave, name='update-leave'),
    path('leave/delete-leave/<int:pk>', views.delete_leave, name='delete-leave'),
    path('leave/list-leave-staff', views.list_leave_nv, name='list-leave-nv'),
    path('leave/leave-remainder/<int:pk>', views.get_leave_remainder, name='leave-remainder'),
    path('leave/leave-infor', views.leave_infor, name='leave-infor'),
    path('leave/export-leave-info/', export_leave_info, name='export-leave-info'),
]