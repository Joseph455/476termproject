import random
from typing import Any
from phenotypes import Venue, Course, Day 
from utils import find_consequitive_integers, TimeTable, find_phenotype_by_id, rank_selection, tournament_selection, pick_center_third
from pprint import pprint



class GATestRunner:
    """This is a test runner for our GA."""
    population: list[TimeTable] = []
    max_population_size = 1000
    max_number_of_generations = 10000
    local_optima_generation = 15

    _generation = 0

    _no_of_cources = 180
    _no_of_days = 12
    _no_of_periods = 10
    _no_of_venues = 10
    _mutation_probablity = 0.5
    _rank_selection_probability = 0.5
    _tournament_size = 3
    _elite: TimeTable = None

    _phenotype: dict[str, list[Course | Venue | Day]] 

    def __perform_mutation(self, child: TimeTable) -> TimeTable:
        """Mutate a childs gene based on some  proberbility."""

        if (random.randrange(1, 100) / 100) <= self._mutation_probablity:

            # swap cources 
            cources_to_mutate = random.choices(list(child.chromosome.keys()), k=2)
            child.chromosome[cources_to_mutate[0]], child.chromosome[cources_to_mutate[1]] = child.chromosome[cources_to_mutate[1]], child.chromosome[cources_to_mutate[0]]

            # mututate day of random cource
            cource = random.choice(list(child.chromosome.keys()))
            day_to_swap_out = list(child.chromosome[cource].keys())[0]
            day_to_swap_to = random.choice([day.id for day in self._phenotype['days'] if day != day_to_swap_out])

            if day_to_swap_to != day_to_swap_out:
                child.chromosome[cource].update({day_to_swap_to: child.chromosome[cource][day_to_swap_out]})
                child.chromosome[cource].pop(day_to_swap_out)

    def __perform_crossover(self, parent_a: TimeTable, parent_b: TimeTable) -> list[TimeTable]:
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

    def __perform_selection(self) -> list[tuple[TimeTable, TimeTable]]:
        """Create a mating pool to be used for crossover."""
        mating_pool = []

        while len(mating_pool) < self.max_population_size:
            parent_1 = tournament_selection(self.population, self._tournament_size)
            parent_2 = tournament_selection(self.population, self._tournament_size)

            # while parent_1.id == parent_2.id:
            #     # just in case we select the same individuals  
            #     parent_2 = tournament_selection(self.population, self._tournament_size)
            
            mating_pool.append((parent_1, parent_2))
        
        return mating_pool

    # def __perform_selection(self) -> list[tuple[TimeTable, TimeTable]]:
    #     """Create a mating pool to be used for crossover."""
    #     mating_pool = []
    #     propability_weights = []
    #     sorted_population = list(sorted(self.population, reverse=True))

    #     for i in range(len(sorted_population)) :
    #         n = i + 1.0

    #         if n == len(self.population):
    #             weight = (1 - self._rank_selection_probability)**(n - 1)
    #         else:
    #             weight = ((1 - self._rank_selection_probability)**(n - 1)) * self._rank_selection_probability

    #         propability_weights.append(weight)
        
    #     while len(mating_pool) < self.max_population_size:
    #         parent_1 = rank_selection(sorted_population=sorted_population, population_wiegth=propability_weights)
    #         parent_2 = rank_selection(sorted_population=sorted_population, population_wiegth=propability_weights)

    #         while parent_1.id == parent_2.id:
    #             # just in case we select the same individuals  
    #             parent_2 = rank_selection(sorted_population=sorted_population, population_wiegth=propability_weights)
            
    #         mating_pool.append((parent_1, parent_2))
        
    #     return mating_pool

    def __generate_initial_population(self) -> None:
        """Randomly generate intial population."""

        # before generating population we need to generate phenotype 
        self._phenotype = self.__generate_phenotypes()

        for i in range(self.max_population_size):
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
                Course(code=f'C{i}', students_population=random.randint(50, 100), required_periods=random.randint(1, 2))
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

    def __evaluate_population(self) -> bool:
        """Check if the termination criteria are met."""

        if (
            self._generation == self.max_number_of_generations or 
            max(self.population).unfitness_score == 0
        ):
            return True

        return False

    def run(self) -> None:
        """Run test GA runner."""
        
        self.__generate_initial_population()
        best_individual = max(self.population)
        worst_individual = min(self.population)
       
        while not self.__evaluate_population(): 
            self._generation += 1
            mating_pool = self.__perform_selection()
            new_population = []

            for match in mating_pool:
                child_1, child_2 = self.__perform_crossover(match[0], match[1])
                self.__perform_mutation(child_1)
                self.__perform_mutation(child_2)

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

if __name__ == '__main__':
    runner = GATestRunner()
    runner.run()

