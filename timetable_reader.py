import csv
from os import read
from termios import VMIN
from typing import Any
from phenotypes import Course, Venue, Day
from utils import TimeTable, find_phenotype_by_id
from pprint import pprint


def _strip_spaces(value: str) -> str:
    """Strip all spaces from string"""
    return value.replace(' ', '') 

def read_timetable_data(
    csv_reader: csv.DictReader,
) -> tuple[TimeTable, dict[str, list[Course | Venue | Day]]]:
    """Extract timetable and phenotype from timetable reader."""
    cource_set = set()
    period_list = []
    venue_set = set()
    day_set = set()

    phenotype = {
        'cources': [],
        'venues': [],
        'days': []
    }

    chromosome: dict[int, dict[int, dict[int, list[int]]]] = {}
    counter = 0
    
    for row in csv_reader:
        counter += 1
        
        if counter == 1:
            continue

        cource, day, venues, period = (
            _strip_spaces(row['cource']).upper(), 
            _strip_spaces(row['day']).upper(), 
            _strip_spaces(row['venues'] or '').upper().split(','), 
            _strip_spaces(row['period']).upper()
        )

        # create cource phenotype
        if cource not in cource_set:
            cource_phenotype = Course(code=cource, students_population=0, required_periods=1)
            phenotype['cources'].append(cource_phenotype)
            cource_set.add(cource)
        else:
            cource_phenotype = list(filter(lambda phen: phen.code == cource, phenotype['cources']))[0]

        # create day phenotype
        if day not in day_set:
            day_phenotype = Day(date=day, periods=[])
            phenotype['days'].append(day_phenotype)
            day_set.add(day)
        else:
            day_phenotype = list(filter(lambda phen: phen.date == day, phenotype['days']))[0]
        
        # add period to day
        if period not in period_list:
            period_list.append(period)
            period_no = period_list.index(period) + 1
        else:
            period_no = period_list.index(period) + 1
        
        if period_no not in day_phenotype.periods:
            day_phenotype.periods.append(period_no)

        # create venue phenotype
        venue_phenotypes = [] 
        for venue in venues:
            venue = venue.replace(',', '')
            if venue:
                if venue not in venue_set:
                    venue_phenotype = Venue(title=venue, capacity=0)
                    phenotype['venues'].append(venue_phenotype)
                    venue_set.add(venue)
                else:
                    venue_phenotype = list(filter(lambda phen: phen.title == venue, phenotype['venues']))[0]

                venue_phenotypes.append(venue_phenotype)
        
        # create timetable chromosome
        chromosome[cource_phenotype.id] = {day_phenotype.id: {venue_phenotype.id: [period_no] for venue_phenotype in venue_phenotypes}}

    return TimeTable(chromosome=chromosome, phenotype=phenotype), phenotype



if __name__ == '__main__':
    file_name = '2022_2023_timetable.csv'

    with open(file_name, mode='r') as csv_file:
        reader = csv.DictReader(f=csv_file, fieldnames=['cource', 'day', 'venues', 'period'])
        timetable, phenotypes = read_timetable_data(reader)

        print(timetable.unfitness_score)
        # pprint(timetable.chromosome)
        # pprint(phenotypes)

