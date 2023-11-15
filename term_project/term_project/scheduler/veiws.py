from django.urls import reverse
from django.views import View, generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.contrib import messages

from term_project.scheduler.models import (
    Schedule, 
    DataSet, 
    CourseModel, 
    CourceDataSet,
    VenueModel,
    VenueDataSet,
)
from term_project.scheduler.forms import DatasetCreationForm


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

        context = {'datasets': DataSet.objects.all().order_by('-date_created')}
        return render(request, 'scheduler/schedule_creation.html', context=context)
