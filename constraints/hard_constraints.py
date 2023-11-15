


def check_hard_constraints(individual, phenotype, score: int = 1) -> int:
    """Resolve hard constraints."""

    from utils import find_phenotype_by_id
    
    total_score = 0
    cource_ids_to_be_scheduled = [course.id for course in phenotype['cources']]
    collision_array = [] 
    
    # all papers must be scheduled
    total_score += (len(cource_ids_to_be_scheduled) - len(list(individual.chromosome.keys()))) * score

    for cource_id, cource_gene in individual.chromosome.items():

        # papers should only be scheduled in a day 
        total_score += score if len(cource_gene.keys()) != 1 else 0

        for day_id, day_gene in cource_gene.items():
            
            for venue_id, venue_gene in day_gene.items():
               
                for index, period in enumerate(venue_gene):
                    
                    # ensure periods are valid phenotype
                    total_score += score if period not in find_phenotype_by_id(phenotype['days'], day_id).periods else 0

                    # avoid schedule collisions
                    if f'{day_id}{venue_id}{period}' in collision_array:
                        total_score += score 
                    else :
                        collision_array.append(f'{day_id}{venue_id}{period}')

                    try:
                        # papers spanning multiple peridos should have adjacent periods
                        total_score += score if venue_gene[index] + 1 > venue_gene[index + 1] else 0
                    except IndexError:
                        continue
    
        
    return total_score
