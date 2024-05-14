import random
from typing import Any
from term_project.scheduler.generic_algorithim.constraints.hard_constraints import check_hard_constraints 
from pprint import pprint


class TimeTable:
    """Class representing a timetable."""
    population_id: int = 1
    chromosome: dict[int, dict[int, dict[int, list[int]]]]
    unfitness_score: int

    def __init__(self, chromosome: dict[int, dict[int, dict[int, list[int]]]], phenotype: Any) -> None:
        """Initialises a new timetable randomly or from chromosome."""
        self.id = TimeTable.population_id
        TimeTable.population_id += 1
        self.chromosome = chromosome
        self._phenotype = phenotype 
        self.calcuate_fitness_score()

    def calcuate_fitness_score(self) -> None:
        """Calculates the fitness score of the timetable."""
        self.unfitness_score = check_hard_constraints(self, self._phenotype)
    
    def chromosome_to_phenotype(self, phenotype: Any) -> Any:
        """Convert chromosome to phenotype data."""
        data = {}
        for cource_id, cource_chromosome in self.chromosome.items():
            cource = find_phenotype_by_id(phenotype['cources'], cource_id)
            data[cource.code] = {}

            for day_id, day_chromosome in cource_chromosome.items():
                day = find_phenotype_by_id(phenotype['days'], day_id)
                data[cource.code][str(day.date)] = {}

                for venue_id, venue_chromosome in day_chromosome.items():
                    venue = find_phenotype_by_id(phenotype['venues'], venue_id)
                    data[cource.code][str(day.date)][venue.title] = venue_chromosome
        
        return data
  
    def __lt__(self, other: "TimeTable") -> bool:
        """Compares the fitness score of two timetables."""
        return self.unfitness_score > other.unfitness_score

    def __gt__(self, other: "TimeTable") -> bool:
        """Compares the fitness score of two timetables."""
        return self.unfitness_score < other.unfitness_score
    
    def __eq__(self, other: "TimeTable") -> bool:
        """Compares the fitness score of two timetables."""
        return self.unfitness_score == other.unfitness_score

    def __le__(self, other: "TimeTable"):
        return self.unfitness_score >= other.unfitness_score
    
    def __ge__(self, other: "TimeTable"):
        return self.unfitness_score <= other.unfitness_score

    def __str__(self) -> str:
        """Returns a string representation of the timetable."""
        return f"TimeTable[id={self.id}, unfitness_score={self.unfitness_score}]"

    def __repr__(self) -> str:
        """Returns a string representation of the timetable."""
        return f"TimeTable[id={self.id}, unfitness_score={self.unfitness_score}]"


def find_consequitive_integers(int_list: list[int], x) -> list[list[int]]:
    """Find list of consequitive integers in a list of intergers."""
    consecutive_count = 0
    consecutive_start = None
    consequitive_intergers = []

    for i in range(len(int_list)):
        if consecutive_count == 0:
            consecutive_start = int_list[i]

        if int_list[i] == consecutive_start + consecutive_count:
            consecutive_count += 1
        else:
            consecutive_count = 0
            consecutive_start = None

        if consecutive_count == x:
            consecutive_start = None
            consecutive_count = 0
            consequitive_intergers.append(int_list[i-x+1: i+1])

    return consequitive_intergers


def tournament_selection(population: list[TimeTable], participant_size: int = 10) -> TimeTable: 
    """Perform tournament selection."""
    qualifyers = random.choices(population=population, k=participant_size)
    return max(qualifyers)


def rank_selection(sorted_population: list[TimeTable], population_wiegth: list[float]) -> TimeTable:
    """Perform rank selection on sorted poulation"""
    return random.choices(sorted_population, weights=population_wiegth, k=1)[0]

def pick_center_third(lst: list[Any]) -> tuple[int, int]:
    """Pick center thired element of a list"""
    third = len(lst) // 3
    start = len(lst) // 2 - third // 2
    end = start + third
    return start, end


def find_phenotype_by_id(phenotype_list, id) -> Any:
    """Find a phenotype by its id."""
    results = list(filter(lambda phenotype: phenotype.id == id, phenotype_list))
    
    if not results:
        print([phenotype_list, id])

    return results[0] if results else None

