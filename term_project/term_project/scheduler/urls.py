from django.urls import path
from term_project.scheduler.veiws import (
    DashboardView, 
    DatasetCreationView,
    DatasetDetailView,
    ScheduleCreationView,
    SchduleMonitorView,
    ScheduleCreationAPIView,
    ScheduleMonitorAPIView,
    ScheduleResultView,
)


app_name = "scheduler"
urlpatterns = [
    path("dashboard/", view=DashboardView.as_view(), name="dashboard"),
    path('datasets/', view=DatasetCreationView.as_view(), name='create_dataset'),
    path('datasets/<pk>/', DatasetDetailView.as_view(), name='dataset_detail'),
    path('schedules/', ScheduleCreationView.as_view(), name='create_schedule'),
    path('schedules-api/', ScheduleCreationAPIView.as_view(), name='create_schedule_api'),
    path('schedules/<pk>/', SchduleMonitorView.as_view(), name='schedule_monitor'),
    path('schedules-api/<pk>/', ScheduleMonitorAPIView.as_view(), name='schedule_monitor_api'),
    path('schedules/<pk>/result/', ScheduleResultView.as_view(), name='schedule_result'),
]
