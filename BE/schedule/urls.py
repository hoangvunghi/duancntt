from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'configchedules', views.ConfigScheduleAPIView,
                basename='config-schedules')
router.register(r'workshifts', views.WorkShiftAPIView, basename='workshifts')
router.register(r'schedules', views.ScheduleAPiView, basename='schedules')
urlpatterns = [
    path('configchedules/using-true/', views.ConfigScheduleUsingTrueAPIView.as_view(),
         name='configschedule-using-true'),
    path('schedule-list/',views.ScheduleListShiftAPIView.as_view(),name="Schedule-list"),
    *router.urls,
    path("schedule/schedule-infor",views.schedule_info,name="schedule_infor"),
]
