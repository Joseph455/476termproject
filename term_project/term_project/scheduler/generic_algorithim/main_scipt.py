from concurrent.futures import ThreadPoolExecutor
import copy
import random
from typing import Any
from pprint import pprint
import concurrent

from django.utils import timezone
from term_project.scheduler.generic_algorithim.phenotypes import Venue, Course, Day
from term_project.scheduler.models import Schedule, ScheduleLog
from term_project.scheduler.generic_algorithim.utils import (
    TimeTable, 
    find_consequitive_integers, 
    find_phenotype_by_id, 
    tournament_selection, 
    pick_center_third,
    check_hard_constraints,
)


class GATestRunner:
    """This is a test runner for our GA."""
    population: list[TimeTable] = []
    max_population_size = 1000
    max_number_of_generations = 10000
    local_optima_generation = 15

    _generation = 0

    _no_of_cources = 150
    _no_of_days = 12
    _no_of_periods = 3
    _no_of_venues = 20
    _mutation_probablity = 0.8
    _tournament_size = 2
    _elite: TimeTable = None

    def __init__(self, phenotype: dict[str, list[Course | Venue | Day]]):
        self._phenotype = phenotype

    def _perform_mutation(self, child: TimeTable) -> TimeTable:
        """Mutate a childs gene based on some  proberbility."""

        if random.random() <= self._mutation_probablity:
            # swap cources 
            cources_to_mutate = random.choices(list(child.chromosome.keys()), k=2)
            child.chromosome[cources_to_mutate[0]], child.chromosome[cources_to_mutate[1]] = child.chromosome[cources_to_mutate[1]], child.chromosome[cources_to_mutate[0]]

        # mututate day of random cource
        if random.random() <= self._mutation_probablity:
            cource = random.choice(list(child.chromosome.keys()))
            day_to_swap_out = list(child.chromosome[cource].keys())[0]
            day_to_swap_to = random.choice([day.id for day in self._phenotype['days'] if day != day_to_swap_out])

            if day_to_swap_to != day_to_swap_out and day_to_swap_to is not None:
                child.chromosome[cource].update({day_to_swap_to: child.chromosome[cource][day_to_swap_out]})
                child.chromosome[cource].pop(day_to_swap_out)

        # swap venue of random cource, day
        if random.random() <= self._mutation_probablity:
            cource = random.choice(list(child.chromosome.keys()))
            day = list(child.chromosome[cource].keys())[0]
            venue_to_out = random.choice(list(child.chromosome[cource][day].keys()))
            venue_to_swap_to = random.choice([venue.id for venue in self._phenotype['venues'] if venue != venue_to_out])
            
            if venue_to_swap_to != venue_to_out:
                child.chromosome[cource][day].update({venue_to_swap_to: child.chromosome[cource][day][venue_to_out]})
                child.chromosome[cource][day].pop(venue_to_out)
        
        # swap period of random cource, day
        if random.random() <= self._mutation_probablity:
            cource = random.choice(list(child.chromosome.keys()))
            day = list(child.chromosome[cource].keys())[0]
            venue = list(child.chromosome[cource][day].keys())[0]
            period_to_swap_out = random.choice(child.chromosome[cource][day][venue])
            day_phenotype: Day = find_phenotype_by_id(self._phenotype['days'], day)
            period_to_swap_in = random.choice([period for period in day_phenotype.periods])
            
            if period_to_swap_out != period_to_swap_in and period_to_swap_in:
                child.chromosome[cource][day][venue].remove(period_to_swap_out)
                child.chromosome[cource][day][venue].append(period_to_swap_in)
        
    def _perform_crossover(self, parent_a: TimeTable, parent_b: TimeTable) -> list[TimeTable]:
        """Crossover parents from a mating pool using partially mapped crossover PMX."""

        parent_a_chormosome_keys = list(parent_a.chromosome.keys())
        parent_b_chormosome_keys = list(parent_b.chromosome.keys())

        # pick sections to crossover 
        parent_a_crossover_section = pick_center_third(parent_a_chormosome_keys)
        parent_b_crossover_section = pick_center_third(parent_b_chormosome_keys)

        child_a_chromosome_keys = (
            parent_a_chormosome_keys[:parent_a_crossover_section[0]] +
            parent_a_chormosome_keys[parent_a_crossover_section[1]:]
        )

        child_b_chromosome_keys = (
            parent_b_chormosome_keys[:parent_b_crossover_section[0]] +
            parent_b_chormosome_keys[parent_b_crossover_section[1]:]
        )

        child_a_chromosomes = {key: parent_a.chromosome[key] for key in child_a_chromosome_keys}
        child_b_chromosomes = {key: parent_b.chromosome[key] for key in child_b_chromosome_keys}
        child_a_chromosomes.update(
            {
                key: parent_b.chromosome[key] 
                for key in parent_b_chormosome_keys[parent_b_crossover_section[0]:parent_b_crossover_section[1]]
            }
        )
        child_b_chromosomes.update(
            {
                key: parent_a.chromosome[key] 
                for key in parent_a_chormosome_keys[parent_a_crossover_section[0]:parent_a_crossover_section[1]]
            }
        )
        
        return [TimeTable(child_a_chromosomes, phenotype=self._phenotype), TimeTable(child_b_chromosomes, phenotype=self._phenotype)]

    def _perform_selection(self) -> list[tuple[TimeTable, TimeTable]]:
        """Create a mating pool to be used for crossover."""
        mating_pool = []

        while len(mating_pool) < self.max_population_size:
            parent_1 = tournament_selection(self.population, self._tournament_size)
            parent_2 = tournament_selection(self.population, self._tournament_size)

            while parent_1.id == parent_2.id:
                # just in case we select the same individuals  
                parent_2 = tournament_selection(self.population, self._tournament_size)
            
            mating_pool.append((parent_1, parent_2))
        
        return mating_pool

    def _generate_initial_population(self) -> None:
        """Randomly generate intial population."""

        # before generating population we need to generate phenotype 
        self._phenotype = self.__generate_phenotypes() if self._phenotype is None else self._phenotype

        for _ in range(self.max_population_size):
            new_individual_chromosome = dict()
            for cource in self._phenotype['cources']:

                # randomly pick the day to schedule the cource
                for day in self._phenotype['days']:
                    consquitive_periods = find_consequitive_integers(day.periods, cource.required_periods)
                    
                    if random.randint(0, 1) == 1 and consquitive_periods:
                        break
                
                if consquitive_periods:
                    periods = random.choice(consquitive_periods)
                else:
                    periods = random.choices(day.periods, k=cource.required_periods)
    
                venues = []
                cource_capacity = cource.students_population

                for venue in self._phenotype['venues']:
                    if random.randint(0, 1) == 1:
                        venues.append(venue)
                        if cource_capacity > venue.capacity:
                            cource_capacity -= venue.capacity
                            continue
                        else:
                            break
                
                if not venues:
                    venues.append(random.choice(self._phenotype['venues']))

                new_individual_chromosome[cource.id] = {day.id: {v.id: periods for v in venues}}

            self.population.append(TimeTable(new_individual_chromosome, phenotype=self._phenotype))

    def __generate_phenotypes(self) -> dict[str, list[Any]]:
        """Generate phenotypes to use in algorithim."""
        phenotype = {
            'cources': [],
            'days': [],
            'venues': [],
        }

        for i in range(1, self._no_of_cources+1):
            phenotype['cources'].append(
                Course(code=f'C{i}', students_population=random.randint(50, 100), required_periods=random.randint(1, 1))
            )

        for i in range(1, self._no_of_days+1):
            phenotype['days'].append(
                Day(
                    date=f'{i}/01/2023', 
                    periods=[x for x in range(1, self._no_of_periods+1)]
                )
            )
        
        for i in range(1, self._no_of_venues+1):
            phenotype['venues'].append(
                Venue(
                    title=f'Venue{i}',
                    capacity=random.randint(80, 150)
                )
            )

        return phenotype

    def _evaluate_population(self) -> bool:
        """Check if the termination criteria are met."""
        best = max(self.population)
        best.calcuate_fitness_score()
        return best.unfitness_score == 0

    def run(self) -> None:
        """Run test GA runner."""
        
        self._generate_initial_population()
        best_individual = max(self.population)
        worst_individual = min(self.population)
       
        while not self._evaluate_population(): 
            self._generation += 1
            mating_pool = self._perform_selection()
            new_population = []

            for match in mating_pool:
                child_1, child_2 = self._perform_crossover(match[0], match[1])
                self._perform_mutation(child_1)
                self._perform_mutation(child_2)

                new_population.append(child_1)
                new_population.append(child_2)

            self.population = new_population

            best_individual = max(self.population)
            worst_individual = min(self.population)

            if self._elite and max(self.population) < self._elite:
                self.population.remove(min(self.population))
                self.population.append(self._elite)
                best_individual = self._elite
            else :
                self._elite = best_individual
           
            pprint([best_individual.unfitness_score, worst_individual.unfitness_score, self._mutation_probablity])

        pprint(best_individual.chromosome)



class GARunner(GATestRunner):

    __log_frequency: int = 10

    def __init__(self, phenotype: dict[str, list[Course | Venue | Day]], schedule_model: Schedule):
        self.schedule_model = schedule_model
        super().__init__(phenotype)

    def _evaluate_population(self) -> bool:
        terminate = super()._evaluate_population()
        print(terminate)
        self.schedule_model.refresh_from_db()
        return terminate or (self.schedule_model.status != Schedule.SCHEDULE_STATUS_PROCESSING)

    def _load_settings(self) -> None:
        """Load GA settings from DB."""
        self.schedule_model.refresh_from_db()
        self.max_population_size = self.schedule_model.ga_settings['population_size']
        self._tournament_size = self.schedule_model.ga_settings['tournament_size']
        self._mutation_probablity = self.schedule_model.ga_settings['mutation_probability']

    def _log_evaluation(self, best_individual: TimeTable, worst_individual: TimeTable) -> None:
        """Log schedule evaluation."""
        self.schedule_model.refresh_from_db()

        if hasattr(self.schedule_model, 'schedulelog'):
            self.schedule_model.schedulelog.current_conflict_score = best_individual.unfitness_score
            self.schedule_model.schedulelog.number_of_generations= self._generation
            self.schedule_model.schedulelog.result = best_individual.chromosome_to_phenotype(phenotype=self._phenotype)
            self.schedule_model.schedulelog.timestamp=timezone.now()
            self.schedule_model.schedulelog.save(
                update_fields=[
                    'current_conflict_score', 'number_of_generations',
                    'result', 'timestamp'
                ]
            )
        else:
            ScheduleLog.objects.create(
                schedule=self.schedule_model,
                initial_conflict_score=worst_individual.unfitness_score,
                current_conflict_score=best_individual.unfitness_score,
                number_of_generations=self._generation,
                result=best_individual.chromosome_to_phenotype(phenotype=self._phenotype),
                timestamp=timezone.now(),
            )


    def run(self) -> TimeTable:
        """Run test GA runner."""
        
        self._load_settings()
        self._generate_initial_population()

        best_individual = max(self.population)
        worst_individual = min(self.population)

        self._elite = copy.deepcopy(best_individual)

        while not self._evaluate_population(): 
            self._generation += 1
            mating_pool = self._perform_selection()
            new_population = []

            for match in mating_pool:
                child_1, child_2 = self._perform_crossover(match[0], match[1])
                self._perform_mutation(child_1)
                self._perform_mutation(child_2)

                new_population.append(child_1)
                new_population.append(child_2)

            self.population = new_population

            with ThreadPoolExecutor(max_workers=10) as executor: 
                # re-evaluate populations
                for individual in self.population:
                    executor.submit(individual.calcuate_fitness_score)

            best_individual = max(self.population)
            worst_individual = min(self.population)

            self._elite.calcuate_fitness_score()

            if best_individual < self._elite:
                # self.population.remove(worst_individual)
                self.population.append(copy.deepcopy(self._elite))
            else:
                self._elite = copy.deepcopy(best_individual)
            
            if (self._generation % self.__log_frequency == 0) or self._generation == 1:
                # log first generation and every other concurrent freq ones
                self._load_settings()
                self._log_evaluation(
                    best_individual=self._elite if self._elite else  best_individual,
                    worst_individual=worst_individual
                )
            
            print([self._elite, worst_individual])

        # log last run
        self._log_evaluation(
            best_individual=self._elite if self._elite else  best_individual,
            worst_individual=worst_individual
        )
        return best_individual

