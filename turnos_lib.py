from datetime import datetime
from deap import base, creator, tools
import calendar
import random


NAMES = ["Ana", "Carlos", "Lucía", "Miguel", "Sofía", "David"]
WEEKS_IN_YEAR = 52
YEAR = 2023

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()


# Funciones auxiliares
def is_valid(individual):
    for i, week in enumerate(individual[:-1]):
        day_worker, night_worker, weekend_worker = week

        # Regla 1
        if day_worker == night_worker or day_worker == weekend_worker:
            return False
        if individual[i + 1][1] != day_worker:
            return False

        # Regla 2
        if night_worker == day_worker or night_worker == weekend_worker:
            return False
        if night_worker in individual[i + 1]:
            return False

        # Regla 3
        if weekend_worker == day_worker or weekend_worker == night_worker:
            return False

    return True


def backtrack(individual):
    if len(individual) == WEEKS_IN_YEAR:
        return True
    workers = list(range(len(NAMES)))
    random.shuffle(workers)
    for day_worker in workers:
        for night_worker in workers:
            for weekend_worker in workers:
                if day_worker != night_worker and day_worker != weekend_worker and night_worker != weekend_worker:
                    new_individual = individual + [[day_worker, night_worker, weekend_worker]]
                    if is_valid(new_individual):
                        if backtrack(new_individual):
                            individual[:] = new_individual
                            return True
    return False


def init_individual():
    individual = []
    attempts = 0
    while not backtrack(individual):
        individual = []
        attempts += 1
        if attempts > 10:  # Limitamos los intentos para evitar ciclos infinitos
            break
    return individual


def evaluate(individual, year=YEAR):  # Hacemos que el año sea parametrizable
    """Función de aptitud que mide cuán equitativa es la distribución durante el año y dentro de cada mes."""
    # Función auxiliar para calcular la varianza
    def calculate_variance(counts, expected):
        return sum([(count - expected) ** 2 for count in counts.values()]) / len(NAMES)

    # Separar trabajadores por tipo de turno
    day_workers = [week[0] for week in individual]
    night_workers = [week[1] for week in individual]
    weekend_workers = [week[2] for week in individual]

    # Calcular la varianza total
    expected_days = len(individual) / len(NAMES)
    year_variance = sum([
        calculate_variance({i: day_workers.count(i) for i in set(day_workers)}, expected_days),
        calculate_variance({i: night_workers.count(i) for i in set(night_workers)}, expected_days),
        calculate_variance({i: weekend_workers.count(i) for i in set(weekend_workers)}, expected_days)
    ])

    # Calcular la varianza dentro de cada mes
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

    # Combinar la varianza total y la varianza mensual para obtener la medida final de desequilibrio
    total_variance = 2 * year_variance + sum(month_variances)

    return total_variance,


def mutate_individual(ind, year=YEAR):
    day_to_mutate = random.randint(0, len(ind) - 1)  # Seleccionamos aleatoriamente una semana para mutar
    attempts = 0
    mutated = False
    while not mutated:
        new_day_schedule = random.sample(range(len(NAMES)), 3)
        ind[day_to_mutate] = new_day_schedule
        if is_valid(ind):
            mutated = True
        attempts += 1
        if attempts > 10:  # Limitamos los intentos para evitar ciclos infinitos
            break
    return ind,


def setup_toolbox():
    global toolbox

    # Reiniciar la toolbox
    toolbox = base.Toolbox()

    # Configuraciones
    toolbox.register("individual", tools.initIterate, creator.Individual, init_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutate_individual)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evaluate)


def convert_to_names(individual):
    named_schedule = []
    for week in individual:
        named_week = [NAMES[day_worker] for day_worker in week]
        named_schedule.append(named_week)
    return named_schedule


def optimize_schedule(names, year=YEAR, generations=200, population_size=100):
    global NAMES
    NAMES = names
    setup_toolbox()

    pop = toolbox.population(n=population_size)
    CXPB, MUTPB, NGEN = 0.7, 0.2, generations

    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    for gen in range(NGEN):
        print(f"-- Generación {gen} --")

        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        # Cruzamiento
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        # Mutación
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Verificar y corregir individuos inválidos
        for child in offspring:
            if not is_valid(child):
                child[:] = init_individual()

        # Evaluar individuos después del cruzamiento y mutación
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Actualizar la población
        pop[:] = offspring

    best_ind = tools.selBest(pop, 1)[0]
    best_named_ind = convert_to_names(best_ind)

    return best_named_ind
