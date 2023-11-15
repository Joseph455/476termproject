from django.db import models
from term_project.users.models import User


class CourseModel(models.Model):
    code = models.CharField(primary_key=True, unique=True, max_length=15, db_index=True)
    population = models.PositiveIntegerField(default=0)


class VenueModel(models.Model):
    title = models.CharField(primary_key=True, unique=True, max_length=20, db_index=True)
    examination_capacity = models.PositiveIntegerField(default=0)    


class DataSet(models.Model):
    title = models.CharField(primary_key=True, unique=True, max_length=250, db_index=True)
    description = models.TextField()
    cources = models.ManyToManyField(CourseModel, through='scheduler.CourceDataSet', through_fields=['dataset', 'cource'])
    venues = models.ManyToManyField(VenueModel, through='scheduler.VenueDataSet', through_fields=['dataset', 'venue'])
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)


class CourceDataSet(models.Model):
    cource = models.ForeignKey(CourseModel, on_delete=models.CASCADE)
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)


class VenueDataSet(models.Model):
    venue = models.ForeignKey(VenueModel, on_delete=models.CASCADE)
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)


class Schedule(models.Model):
    SCHEDULE_STATUS_PROCESSING = 0
    SCHEDULE_STATUS_DONE = 1
    SCHEDULE_STATUS_STOPPED = 2
    SCHEDULE_STATUS_CANCLED = 3

    SCHEDULE_STATUS_CHOICES = (
        (SCHEDULE_STATUS_PROCESSING, 'Processing'),
        (SCHEDULE_STATUS_DONE, 'Done'),
        (SCHEDULE_STATUS_STOPPED, 'Stopped'),
        (SCHEDULE_STATUS_CANCLED, 'Cancled'),
    )

    DEFAULT_SCHEDULE_SETTINGS = {
        'mutation_probability': 0.3,
        'population_size': 200,
        'tournament_size': 3,
    }

    title = models.CharField(primary_key=True, unique=True, max_length=250, db_index=True)
    status = models.PositiveIntegerField(choices=SCHEDULE_STATUS_CHOICES, default=SCHEDULE_STATUS_PROCESSING)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    date_created = models.DateTimeField(auto_now_add=True)
    final_result = models.JSONField(null=True)
    ga_settings = models.JSONField(default=DEFAULT_SCHEDULE_SETTINGS)


class ScheduleLog(models.Model):
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE)
    initial_conflict_score = models.PositiveIntegerField()
    current_conflict_score = models.PositiveIntegerField()
    number_of_generations = models.PositiveBigIntegerField(default=0)
    result = models.JSONField()
    timestamp = models.DateTimeField(auto_now=True)

