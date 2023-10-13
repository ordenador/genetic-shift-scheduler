from datetime import datetime
from deap import base, creator, tools
import calendar
import random


# List of names of the workers
NAMES = ["Ana", "Carlos", "Lucía", "Miguel", "Sofía", "David"]
# Number of weeks in a year
WEEKS_IN_YEAR = 52
# Year for which the schedule is being optimized
YEAR = 2023

# DEAP (Distributed Evolutionary Algorithms in Python) is a framework for prototyping and testing evolutionary algorithms.
# It provides a set of tools and techniques to design evolutionary algorithms without having to start from scratch.
# Here, we are using DEAP to implement a genetic algorithm for optimizing a shift schedule.

# In DEAP, we need to create types for fitness and individuals.
# Fitness is a measure of how good a solution (individual) is.
# Here, we are creating a fitness type named 'FitnessMin'. 
# This fitness type is used to evaluate the individuals in our population. 
# The weights parameter is used to define a minimization (-1.0) or maximization (1.0) problem.
# In our case, we want to minimize the imbalance in the shift schedule, so we use -1.0.
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

# An individual represents a potential solution to our problem. 
# In our case, an individual is a list with a 'FitnessMin' property.
# The list contains the shift schedule for the entire year.
# Each element of the list is a week, and each week is a list of three integers representing the workers for each shift.
creator.create("Individual", list, fitness=creator.FitnessMin)

# The toolbox is a DEAP object that contains the evolutionary operators.
# We will register our functions to this toolbox later.
toolbox = base.Toolbox()


def is_valid(individual):
    """
    This function checks if a schedule is valid according to the problem rules.
    The rules are:
    1. A worker cannot work two shifts in the same week.
    2. The day worker of the current week must be the night worker of the next week.
    3. The night worker of the current week cannot work in the next week.
    :param individual: list of weeks, where each week is a list of three integers representing the workers
    :return: True if the schedule is valid, False otherwise
    """
    for i, week in enumerate(individual[:-1]):
        day_worker, night_worker, weekend_worker = week

        # Rule 1: A worker cannot work two shifts in the same week
        if day_worker == night_worker or day_worker == weekend_worker:
            return False
        # Rule 1: The day worker of the current week must be the night worker of the next week
        if individual[i + 1][1] != day_worker:
            return False

        # Rule 2: A worker cannot work two shifts in the same week
        if night_worker == day_worker or night_worker == weekend_worker:
            return False
        # Rule 2: The night worker of the current week cannot work in the next week
        if night_worker in individual[i + 1]:
            return False

        # Rule 3: A worker cannot work two shifts in the same week
        if weekend_worker == day_worker or weekend_worker == night_worker:
            return False

    return True


def backtrack(individual):
    """
    This recursive function generates a valid schedule.
    It uses a backtracking algorithm, which is a type of depth-first search.
    The algorithm tries all possible combinations of workers for each week.
    If it finds a valid schedule, it stops and returns True.
    If it cannot find a valid schedule, it backtracks and tries a different combination.
    :param individual: list of weeks, where each week is a list of three integers representing the workers
    :return: True if a valid schedule has been generated, False otherwise
    """
    if len(individual) == WEEKS_IN_YEAR:
        return True
    workers = list(range(len(NAMES)))
    random.shuffle(workers)
    for day_worker in workers:
        for night_worker in workers:
            for weekend_worker in workers:
                # Check if the workers are different for the current week
                if day_worker != night_worker and day_worker != weekend_worker and night_worker != weekend_worker:
                    new_individual = individual + [[day_worker, night_worker, weekend_worker]]
                    # Check if the new schedule is valid
                    if is_valid(new_individual):
                        # If the new schedule is valid, continue with the next week
                        if backtrack(new_individual):
                            individual[:] = new_individual
                            return True
    return False


def init_individual():
    """
    This function generates a valid schedule.
    It uses the backtrack function to generate a valid schedule.
    If the backtrack function cannot generate a valid schedule after 10 attempts, it stops and returns an empty list.
    :return: list of weeks, where each week is a list of three integers representing the workers
    """
    individual = []
    attempts = 0
    while not backtrack(individual):
        individual = []
        attempts += 1
        # Limit the attempts to avoid infinite loops
        if attempts > 10:
            break
    return individual


def evaluate(individual, year=YEAR):
    """
    This fitness function measures how equitable the distribution is throughout the year and within each month.
    It calculates the variance of the number of shifts for each worker.
    The variance is a measure of how spread out the numbers are.
    :param individual: list of weeks, where each week is a list of three integers representing the workers
    :param year: year for which the schedule is being optimized
    :return: tuple with a single element, which is the imbalance measure of the schedule
    """
    # Helper function to calculate the variance
    def calculate_variance(counts, expected):
        return sum([(count - expected) ** 2 for count in counts.values()]) / len(NAMES)

    # Separate workers by shift type
    day_workers = [week[0] for week in individual]
    night_workers = [week[1] for week in individual]
    weekend_workers = [week[2] for week in individual]

    # Calculate the total variance
    expected_days = len(individual) / len(NAMES)
    year_variance = sum([
        calculate_variance({i: day_workers.count(i) for i in set(day_workers)}, expected_days),
        calculate_variance({i: night_workers.count(i) for i in set(night_workers)}, expected_days),
        calculate_variance({i: weekend_workers.count(i) for i in set(weekend_workers)}, expected_days)
    ])

    # Calculate the variance within each month
    month_variances = []
    for month in range(1, 13):
        last_day = calendar.monthrange(year, month)[1]
        first_week = datetime(year, month, 1).isocalendar()[1]
        last_week = datetime(year, month, last_day).isocalendar()[1]

        month_day_workers = day_workers[first_week-1:last_week]
        month_night_workers = night_workers[first_week-1:last_week]
        month_weekend_workers = weekend_workers[first_week-1:last_week]

        weeks_in_month = last_week - first_week + 1
        expected_days_in_month = weeks_in_month / len(NAMES)
        month_variances.append(sum([
            calculate_variance({i: month_day_workers.count(i) for i in set(month_day_workers)}, expected_days_in_month),
            calculate_variance({i: month_night_workers.count(i)
                               for i in set(month_night_workers)}, expected_days_in_month),
            calculate_variance({i: month_weekend_workers.count(i)
                               for i in set(month_weekend_workers)}, expected_days_in_month)
        ]))

    # Combine the total variance and the monthly variance to get the final imbalance measure
    total_variance = 2 * year_variance + sum(month_variances)

    return total_variance,


def mutate_individual(ind, year=YEAR):
    """
    This function mutates a schedule.
    Mutation is an evolutionary operator that introduces diversity in the population.
    It randomly selects a week and changes the workers for that week.
    If the new schedule is not valid, it tries again up to 10 times.
    :param ind: list of weeks, where each week is a list of three integers representing the workers
    :param year: year for which the schedule is being optimized
    :return: tuple with a single element, which is the mutated schedule
    """
    day_to_mutate = random.randint(0, len(ind) - 1)  # Randomly select a week to mutate
    attempts = 0
    mutated = False
    while not mutated:
        new_day_schedule = random.sample(range(len(NAMES)), 3)
        ind[day_to_mutate] = new_day_schedule
        # Check if the new schedule is valid
        if is_valid(ind):
            mutated = True
        attempts += 1
        # Limit the attempts to avoid infinite loops
        if attempts > 10:
            break
    return ind,


def setup_toolbox():
    """
    This function sets up the DEAP toolbox.
    It registers the functions for creating individuals and populations, and for the evolutionary operators.
    """
    global toolbox

    # Reset the toolbox
    toolbox = base.Toolbox()

    # Register the functions
    toolbox.register("individual", tools.initIterate, creator.Individual, init_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutate_individual)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evaluate)


def convert_to_names(individual):
    """
    This function converts a schedule from a list of indices to a list of names.
    :param individual: list of weeks, where each week is a list of three integers representing the workers
    :return: list of weeks, where each week is a list of three names representing the workers
    """
    named_schedule = []
    for week in individual:
        named_week = [NAMES[day_worker] for day_worker in week]
        named_schedule.append(named_week)
    return named_schedule


def optimize_schedule(names, year=YEAR, generations=200, population_size=100):
    """
    This function optimizes a shift schedule.
    It uses a genetic algorithm to find the best schedule.
    The algorithm evolves a population of schedules over a number of generations.
    In each generation, it selects the best schedules, applies crossover and mutation, and creates a new population.
    :param names: list of the workers' names
    :param year: year for which the schedule is being optimized
    :param generations: number of generations of the population
    :param population_size: size of the population
    :return: list of weeks, where each week is a list of three names representing the workers
    """
    global NAMES
    NAMES = names
    setup_toolbox()

    pop = toolbox.population(n=population_size)
    CXPB, MUTPB, NGEN = 0.7, 0.2, generations

    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    for gen in range(NGEN):
        print(f"-- Generation {gen} --")

        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        # Crossover
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        # Mutation
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Check and correct invalid schedules
        for child in offspring:
            if not is_valid(child):
                child[:] = init_individual()

        # Evaluate the schedules after crossover and mutation
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the population
        pop[:] = offspring

    best_ind = tools.selBest(pop, 1)[0]
    best_named_ind = convert_to_names(best_ind)

    return best_named_ind


