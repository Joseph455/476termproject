from config import celery_app
from term_project.scheduler.models import Schedule
from term_project.scheduler.generic_algorithim import phenotypes
from term_project.scheduler.generic_algorithim.main_scipt import GARunner
from term_project.scheduler.generic_algorithim.utils import TimeTable


@celery_app.task(
    name="solve_timetable_problem_task", 
    soft_time_limit=60 * 60, 
    task_time_limit=(60 * 60) + (60*10)
)
def solve_timetable_problem_task(schedule_title: str):
    """Run GA algorithim on schedule data from DB.""" 

    schedule = Schedule.objects.filter(
        title=schedule_title,
        status=Schedule.SCHEDULE_STATUS_PROCESSING,
    ).first()

    if not schedule:
        return

    # NA beans but lets reset phenotype classes to avoid a bug
    phenotypes.Course.__class_id = 1
    phenotypes.Venue.__class_id = 1
    phenotypes.Day.__class_id = 1
    TimeTable.population_id = 1

    phenotype_data = {
        'cources': [
            phenotypes.Course(
                id=index,
                code=cource.code,
                students_population=cource.population
            ) 
            for index, cource in enumerate(schedule.dataset.cources.all(), start=1)
        ],
        'venues': [
            phenotypes.Venue(
                id=index,
                title=venue.title,
                capacity=venue.examination_capacity,
            )
            for index, venue in enumerate(schedule.dataset.venues.all(), start=1)
        ],
        'days': [
            phenotypes.Day(
                id=index,
                date=day.date,
                periods=[period._id for period in day.periods.all()]
            )
            for index, day in enumerate(schedule.days.all(), 1)
        ]
    }
    
    try:
        runner = GARunner(phenotype_data, schedule_model=schedule)
        result =  runner.run()
        result.calcuate_fitness_score()
    except:
        return solve_timetable_problem_task(schedule_title)
    schedule.final_result = result.chromosome_to_phenotype(phenotype_data)
    schedule.status = (
        Schedule.SCHEDULE_STATUS_DONE 
        if (result.unfitness_score == 0) else 
        Schedule.SCHEDULE_STATUS_STOPPED
    )

    schedule.save(update_fields=['final_result', 'status'])

