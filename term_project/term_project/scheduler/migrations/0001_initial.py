# Generated by Django 4.2.7 on 2023-11-14 22:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CourceDataSet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ],
        ),
        migrations.CreateModel(
            name="CourseModel",
            fields=[
                (
                    "code",
                    models.CharField(db_index=True, max_length=15, primary_key=True, serialize=False, unique=True),
                ),
                ("population", models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="DataSet",
            fields=[
                (
                    "title",
                    models.CharField(db_index=True, max_length=250, primary_key=True, serialize=False, unique=True),
                ),
                ("description", models.TextField()),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("cources", models.ManyToManyField(through="scheduler.CourceDataSet", to="scheduler.coursemodel")),
                (
                    "created_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Schedule",
            fields=[
                (
                    "title",
                    models.CharField(db_index=True, max_length=250, primary_key=True, serialize=False, unique=True),
                ),
                (
                    "status",
                    models.PositiveIntegerField(
                        choices=[
                            (0, "Processing Schedule"),
                            (1, "Done"),
                            (2, "Stopped Schedule"),
                            (3, "Cancled Schedule"),
                        ],
                        default=0,
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("final_result", models.JSONField(null=True)),
                (
                    "ga_settings",
                    models.JSONField(
                        default={"mutation_probability": 0.1, "population_size": 200, "tournament_size": 3}
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.CreateModel(
            name="VenueModel",
            fields=[
                (
                    "title",
                    models.CharField(db_index=True, max_length=20, primary_key=True, serialize=False, unique=True),
                ),
                ("examination_capacity", models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="VenueDataSet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("dataset", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="scheduler.dataset")),
                ("venue", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="scheduler.venuemodel")),
            ],
        ),
        migrations.CreateModel(
            name="ScheduleLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("initial_conflict_score", models.PositiveIntegerField()),
                ("current_conflict_score", models.PositiveIntegerField()),
                ("number_of_generations", models.PositiveBigIntegerField(default=0)),
                ("result", models.JSONField()),
                ("timestamp", models.DateTimeField(auto_now=True)),
                (
                    "schedule",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="scheduler.schedule"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="dataset",
            name="venues",
            field=models.ManyToManyField(through="scheduler.VenueDataSet", to="scheduler.venuemodel"),
        ),
        migrations.AddField(
            model_name="courcedataset",
            name="cource",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="scheduler.coursemodel"),
        ),
        migrations.AddField(
            model_name="courcedataset",
            name="dataset",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="scheduler.dataset"),
        ),
    ]
