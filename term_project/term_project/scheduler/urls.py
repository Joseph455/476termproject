from django.urls import path
from term_project.scheduler.veiws import (
    DashboardView, 
    DatasetCreationView,
    DatasetDetailView
)


app_name = "scheduler"
urlpatterns = [
    path("dashboard/", view=DashboardView.as_view(), name="dashboard"),
    path('datasets/', view=DatasetCreationView.as_view(), name='create_dataset'),
    path('datasets/<pk>/', DatasetDetailView.as_view(), name='dataset_detail'),
]
