from typing import Any
from django.urls import reverse
from django.views import View, generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response 
from term_project.scheduler.models import (
    Schedule, 
    DataSet, 
    CourseModel, 
    CourceDataSet,
    VenueModel,
    VenueDataSet,
    SchedulePeriod,
    ScheduleDay,
)
from term_project.scheduler.forms import (
    DatasetCreationForm, 
    ScheduleCreationForm,
    SchdeduleCreationSerializer,
    ScheduleSerializer,
)
from term_project.scheduler.tasks import solve_timetable_problem_task
from term_project.users.admin import User


class DashboardView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Get dashboard page."""

        context = {
            'schedules': Schedule.objects.filter(
                created_by=self.request.user
            ).order_by('-date_created'),
            'datasets': DataSet.objects.all().order_by('-date_created')
        }
        
        return render(request, 'scheduler/dashboard.html', context=context)


class DatasetCreationView(LoginRequiredMixin, View):
    form = DatasetCreationForm

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Render dataset creation page."""
        return render(request, 'scheduler/create_dataset.html', context={'form': self.form})


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Create dataset view."""
        form = self.form(data=request.POST, files=request.FILES)
        if form.is_valid():
            # create dataset 
            dataset_model = DataSet.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data.get('description'),
                created_by=self.request.user,   
            )

            # create cources 
            for cource in form.cleaned_data['dataset_file']['cources']:
                cource_model, _ = CourseModel.objects.update_or_create(
                    code=cource['cource_code'].upper(),
                    defaults={'population': cource['population']}
                )
                CourceDataSet.objects.create(cource=cource_model, dataset=dataset_model)
            
            # create venues
            for venue in form.cleaned_data['dataset_file']['venues']:
                venue_model, _ = VenueModel.objects.update_or_create(
                    title=venue['venue_code'].upper(),
                    defaults={'examination_capacity': venue['examination_capacity']}
                )
                VenueDataSet.objects.create(venue=venue_model, dataset=dataset_model)
            
            # redirect to dataset view page 
            return redirect(reverse('scheduler:dataset_detail', args=[dataset_model.pk]))
        return render(request, 'scheduler/create_dataset.html', context={'form': form})


class DatasetDetailView(LoginRequiredMixin, generic.DetailView):
    model = DataSet
    template_name = 'scheduler/dataset_detail.html'


class ScheduleCreationView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Display Schedule creation view."""

        schedule_form = ScheduleCreationForm()
        context = {
            'datasets': DataSet.objects.all().order_by('-date_created'), 
            'schedule_form': schedule_form
        }
        return render(request, 'scheduler/schedule_creation.html', context=context)


class ScheduleCreationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = User.objects.first()
        
        serializer = SchdeduleCreationSerializer(data=request.data)
        if serializer.is_valid():
            # create schdeule 
            dataset = DataSet.objects.filter(title=serializer.data['dataset']).first()
            schedule_record = Schedule.objects.create(
                title=serializer.data['title'], 
                dataset=dataset, 
                created_by=user
            )

            # create periods
            for index, period in enumerate(serializer.data['periods']):
                SchedulePeriod.objects.create(
                    start_time=period['start_time'], 
                    end_time=period['end_time'],
                    _id=index+1,
                    schedule=schedule_record,
                )

            # create days
            for day in serializer.data['days']:
                day_record = ScheduleDay.objects.create(
                    date=day['date'],
                    schedule=schedule_record,
                )
                period_records = []
                for period in day['periods']:
                    period_records.append(
                        SchedulePeriod.objects.filter(
                            start_time=period['start_time'],
                            end_time=period['end_time'],
                            schedule=schedule_record,
                        ).first()
                    )
                day_record.periods.set(period_records)
                day_record.save()
            
            solve_timetable_problem_task.delay(schedule_record.pk)
            return Response(
                data={
                    'message': 'Schedule Creation Succsessful', 
                    'redirect': reverse('scheduler:schedule_monitor', args=[schedule_record.pk])
                }, 
                status=201
            )


        return Response(data={'message': 'SChedule Creation Failed'}, status=401)


class SchduleMonitorView(LoginRequiredMixin, generic.DetailView):
    model = Schedule
    template_name = 'scheduler/schdeule_monitor.html'


class ScheduleMonitorAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        schedule_record = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        serializer = ScheduleSerializer(instance=schedule_record)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        schedule_record = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        serializer = ScheduleSerializer(
            instance=schedule_record, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data)


class ScheduleResultView(LoginRequiredMixin, generic.DetailView):
    model = Schedule
    template_name = 'scheduler/schedule_result.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data['periods'] = data['schedule'].periods.all().order_by('_id')
        return data