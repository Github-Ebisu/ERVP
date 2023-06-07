# -*- coding: utf-8 -*-
import os
import io
import random
from csv import DictWriter

from .utils import *  
from .priority_queue import PriorityQueue

def generate_individual_evenly(num_vehicles, num_customers):
    """Generate an individual by distributing customers evenly across vehicles.
    
    Args:
        num_vehicles: The number of vehicles.
        num_customers: The number of customers.
        
    Returns:
        A list of lists, where each sublist represents a vehicle and its assigned customers.
    """

    # Create a list of customer numbers and shuffle it
    customers = list(range(1, num_customers + 1))

    # Initialize the individual
    individual = []

    random.shuffle(customers)
    individual = [customers[i::num_vehicles] for i in range(num_vehicles)]
    
    return individual
    
def generate_individual_randomly(num_vehicles, num_customers):
    """Generate an individual by randomly assigning customers to vehicles.
    
    Args:
        num_vehicles: The number of vehicles.
        num_customers: The number of customers.
        
    Returns:
        A list of lists, where each sublist represents a vehicle and its assigned customers.
    """
    
    # Initialize an empty individual with a list for each vehicle
    individual = [[] for _ in range(num_vehicles)]
    
    # Create a list of customers and shuffle it
    customers = list(range(1, num_customers + 1))
    random.shuffle(customers)
    
    for customer in customers:
        # Assign the customer to a random vehicle
        vehicle = random.randint(0, num_vehicles - 1)
        individual[vehicle].append(customer)
    
    return individual

# ************************************************************************
# ***************************** Operators ********************************

# crossover
def cx_partially_matched(ind1, ind2):
    """Partially Matched Crossover (PMX)
    
    Args:
        ind1: The first individual participating in the crossover.
        ind2: The second individual participating in the crossover.
        
    Returns:
        A tuple of two individuals.
    """
    
    route_lengths_1 = [len(route) for route in ind1]
    route_lengths_2 = [len(route) for route in ind2]
    flat_ind1 = [node - 1 for route in ind1 for node in route]
    flat_ind2 = [node - 1 for route in ind2 for node in route]
    
    size = min(len(flat_ind1), len(flat_ind2))
    pos1, pos2 = [0] * size, [0] * size

    # Initialize the position of each index in the individuals
    for i in range(size):
        pos1[flat_ind1[i]] = i
        pos2[flat_ind2[i]] = i
    
    # Choose crossover points
    cxpoint1 = random.randint(0, size)
    cxpoint2 = random.randint(0, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else:  # Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1

    # Apply crossover between cx points
    for i in range(cxpoint1, cxpoint2):
        # Keep track of the selected values
        temp1 = flat_ind1[i]
        temp2 = flat_ind2[i]
        # Swap the matched value
        flat_ind1[i], flat_ind1[pos1[temp2]] = temp2, temp1
        flat_ind2[i], flat_ind2[pos2[temp1]] = temp1, temp2
        # Position bookkeeping
        pos1[temp1], pos1[temp2] = pos1[temp2], pos1[temp1]
        pos2[temp1], pos2[temp2] = pos2[temp2], pos2[temp1]

    # Increment node values back to original range
    flat_ind1 = [node + 1 for node in flat_ind1]
    flat_ind2 = [node + 1 for node in flat_ind2]
    

    ind1_reconstructed = reconstruct_individual(flat_ind1, route_lengths_1)
    ind2_reconstructed = reconstruct_individual(flat_ind2, route_lengths_2)
    
    return ind1_reconstructed, ind2_reconstructed

def two_opt(route, distance_matrix):
    """
    Perform 2-opt local search on a given route to optimize it.
    
    Args:
        route: A list of integers representing the customers in the route.
        distance_matrix: A 2D list or numpy array containing the distances between nodes.
    
    Returns:
        A list of integers representing the optimized route.
    """
    _route = [0] + route + [0]
    
    improved = True
    while improved:
        improved = False
        for i in range(1, len(_route) - 2):
            for j in range(i + 1, len(_route) - 1):
                
                # Calculate the cost difference between the old route and the new route obtained by swapping edges
                old_cost = distance_matrix[_route[i - 1]][_route[i]] + distance_matrix[_route[j]][_route[j + 1]]
                new_cost = distance_matrix[_route[i - 1]][_route[j]] + distance_matrix[_route[i]][_route[j + 1]]
                if new_cost < old_cost:
                    _route[i:j + 1] = reversed(_route[i:j + 1])
                    improved = True
    
    # Remove depots from the endpoints
    _route = _route[1:-1]
    return _route

def calculate_total_distance(route, distance_matrix):
    """Calculate the total distance of a route based on the global distance matrix."""
    total_distance = 0
    extended_route = route
    if route[0] != 0 or route[-1] != 0:
        extended_route = [0] + route + [0]
    for i in range(len(extended_route) - 1):
        total_distance += distance_matrix[extended_route[i]][extended_route[i + 1]]
    return total_distance


def simple_repair(initial_route, battery_capacity, energy_consumption, distance_matrix, station_list):
    """
    Repair the given route by ensuring the vehicle has enough energy to reach a charging station from each node.

    Args:
        initial_route (list): The initial route that needs to be repaired.
        battery_capacity (float): The capacity of the vehicle's battery.
        energy_consumption (float): The energy consumption per unit distance.
        distance_matrix (list of lists): A matrix representing the distances between each pair of nodes.
        station_list (list): A list of charging station indices.
    
    Returns:
        list: The repaired route, which ensures that the vehicle has enough energy to reach a charging station from each node.
    """
    route = initial_route.copy()

    if len(route) == 0 or len(route) == 1:
        return route
    repaired_route = [route.pop(0)]
    current_node = repaired_route[-1]
    next_node = route[0]

    # Calculate the remaining energy after departing from the first node
    energy_left = battery_capacity - energy_consumption * distance_matrix[0][current_node]
    
    while route:
        # Update the energy left after moving to the next node
        updated_energy_left = energy_left - energy_consumption * distance_matrix[current_node][next_node]
        nearest_station_to_next = find_nearest_station(next_node, distance_matrix, station_list)

        # Check if there is enough energy left to reach the nearest station from the next node
        if updated_energy_left >= energy_consumption * distance_matrix[next_node][nearest_station_to_next]:
            repaired_route.append(next_node)
            route.pop(0)
            next_node = route[0] if len(route) > 0 else 0
            current_node = repaired_route[-1]
            energy_left = updated_energy_left
        else:
            # Find stations reachable from the current node
            reachable_stations_from_current = [int(station) for station in station_list if energy_left >= energy_consumption * distance_matrix[current_node][int(station)]]
            if not reachable_stations_from_current:
                # if there is no reachable stations from the current node, we would try insert station before the current
                index = repaired_route.index(current_node)
                prev_node = 0 if index == 0 else repaired_route[index - 1]
                
                prev_energy_left = energy_left + energy_consumption * distance_matrix[current_node][prev_node] 
                reachable_stations_from_prev_node = [int(station) for station in station_list if prev_energy_left >= energy_consumption * distance_matrix[prev_node][int(station)]]
                _nearest_station_to_current_node = find_nearest_station(current_node, distance_matrix, reachable_stations_from_prev_node)

                # insert a station before the current node
                repaired_route.insert(index, _nearest_station_to_current_node)
                energy_left = battery_capacity - energy_consumption * distance_matrix[_nearest_station_to_current_node][current_node] 
                
                reachable_stations_from_current = [int(station) for station in station_list if energy_left >= energy_consumption * distance_matrix[current_node][int(station)]]
            nearest_station_to_next = find_nearest_station(next_node, distance_matrix, reachable_stations_from_current)

            repaired_route.append(nearest_station_to_next)
            energy_left = battery_capacity
            current_node = repaired_route[-1]

    # we have to check whether the energy left can support the vehicle to return back to the depot
    if energy_left < energy_consumption * distance_matrix[current_node][0]:
        nearest_station_to_current = find_nearest_station(current_node, distance_matrix, station_list)
        repaired_route.append(nearest_station_to_current)
    
    return repaired_route
    

# ************************************************************************
# ******************************** GA ************************************

def local_search(individual, instance):
    '''Incooperate several local search opereators
    
    Args:
        individual: A list of routes. Each route is a list of nodes.
        instance: the benchmark instance got from the original data
    
    Returns:
        a tuple contains a improved individual and the corresponding cost
    '''
    battery_capacity = instance.battery_capacity
    energy_consumption = instance.energy_consumption
    distance_matrix = instance.distance_matrix
    station_list = instance.station_list

    # 2-opt
    optimized_individual = []
    for route in individual:
        if len(route) <= 1:
            optimized_individual.append(route)
            continue

        # When the size of the route is relatively small, we can even list all possible sequences, 
        # and then pick up the route with the smallest total distance
        route_01 = two_opt(route, distance_matrix)
        
        shuffled_route = route[:]
        random.shuffle(shuffled_route)
        
        route_02 = two_opt(shuffled_route, distance_matrix)

        route_candidates = [route_01, route_02]
        best_route = min(route_candidates, key=lambda x: calculate_total_distance(x, distance_matrix))
        optimized_individual.append(best_route)

    # simple repair (ZGA)
    original_individual = optimized_individual
    repaired_individual = []
    for route in original_individual:
        repaired_route = simple_repair(route, battery_capacity, energy_consumption, distance_matrix, station_list)
        repaired_individual.append(repaired_route)

    cost = fitness_evaluation(repaired_individual, distance_matrix)
    
    return (repaired_individual, cost)

    
def run_GA(instance, seed, pop_size, n_gen, cx_prob, mut_prob, indpb, result_dir, is_export_csv=True):
    random.seed(seed)
                           
    CANDIDATES = PriorityQueue()
    PLAIN_CANDIDATES_SET = set()
    CANDIATES_POOL_SIZE = int(0.5 * pop_size)

    num_vehicles =  instance.num_of_vehicles
    num_customers = instance.dimension - 1
    capacity = instance.capacity
    demands = instance.demands
    station_list = instance.station_list
    
    csv_data = []
    
    # population initialization
    pop = []
    init_pop_randomly = [generate_individual_randomly(num_vehicles, num_customers) for _ in range(int(pop_size * 0.8))]
    init_pop_evenly = [generate_individual_evenly(num_vehicles, num_customers) for _ in range(int(pop_size * 0.2))]
    pop.extend(init_pop_randomly)
    pop.extend(init_pop_evenly)

    best_solution = []
    best_cost = 0.0
    
    print('----------------Start of evolution----------------')
    for gen in range(n_gen):
        print(f'---- Generation {gen} ----')
        
        offspring_after_crossover = []
        for ind1, ind2 in zip(pop[::2], pop[1::2]):
            if random.random() < cx_prob:
                child1, child2 = cx_partially_matched(ind1, ind2)
                offspring_after_crossover.append(child1)
                offspring_after_crossover.append(child2)   


        stats_num_candidates_added = 0
        
        pop_pool = pop + offspring_after_crossover
        for individual in pop_pool:
            if is_capacity_feasible(individual, capacity, demands):
                string_individual = '|'.join('-'.join(str(element) for element in sublist) for sublist in individual)
                if string_individual not in PLAIN_CANDIDATES_SET:
                    stats_num_candidates_added += 1
                    PLAIN_CANDIDATES_SET.add(string_individual)
                    optimized_individual, cost = local_search(individual, instance)
                    CANDIDATES.push(optimized_individual, cost)
        candidates_size = CANDIDATES.size()
        if candidates_size > CANDIATES_POOL_SIZE:
            CANDIDATES.remove_elements(candidates_size - CANDIATES_POOL_SIZE)
            candidates_size = CANDIDATES.size()
    
        # Elites Population
        elites = CANDIDATES.peek(1000)

        # Statistical Data
        size = len(elites)
        fits = []
        mean = 0
        std  = 0.0
        min_fit = None
        max_fit = None

        if size == 0:
            print('  No candidates')
        else:
            fits = [fit for fit, ind in elites]
            mean = sum(fits) / size
            min_fit = min(fits)
            max_fit = max(fits)

        if size > 1:
            std = (sum((x - mean) ** 2 for x in fits) / (size - 1)) ** 0.5
        else:
            std = 0.0
        print(f'  Min {min_fit}') # the best result of each generation
        print(f'  Max {max_fit}')
        print(f'  Mean {mean}')   # Reflect the direction of population evolution 
        print(f'  Stdev {std}')
        
        min_individual = [] 
        min_fitness = None
        
        if size != 0:
            min_fitness, min_individual = CANDIDATES.peek(1)[0]
        best_solution = min_individual
        best_cost = min_fitness
        # Write data to holders for exporting results to CSV file
        if is_export_csv:
            csv_row = {
                'generation': gen,
                'min': min_fit,
                'max': max_fit,
                'mean': mean,
                'stdev': std,
            }
            csv_data.append(csv_row)

        pop = []  
        elites = [ind for fit, ind in elites[:500]]
        elites.extend(CANDIDATES.random_elements(1000))
        elites_without_stations = []
        for ind in elites:
            individual_without_station = []
            for route in ind:
                route_without_stations = [node for node in route if str(node) not in station_list]
                individual_without_station.append(route_without_stations)
            elites_without_stations.append(individual_without_station)       
        pop.extend(elites_without_stations)
        
        num_left = pop_size - len(elites_without_stations)
        random.shuffle(pop_pool)
        individuals_from_pop_pool = pop_pool[:int(num_left * 0.7)]
        
        individuals_from_immigration = []
        individuals_evenly = [generate_individual_evenly(num_vehicles, num_customers) for _ in range(int(num_left * 0.1))]
        individuals_randomly = [generate_individual_randomly(num_vehicles, num_customers) for _ in range(int(num_left * 0.2))]
        individuals_from_immigration.extend(individuals_evenly)
        individuals_from_immigration.extend(individuals_randomly)
        
        pop.extend(individuals_from_pop_pool)
        pop.extend(individuals_from_immigration)
    
    print('------------End of (successful) evolution------------', end='\n\n') 

    csv_file = ''
    if is_export_csv:
        csv_file_name = f'{instance.name}_seed{seed}__pS{pop_size}_nG{n_gen}.csv'
        csv_file_name = os.path.basename(csv_file_name)
        csv_file = os.path.join(result_dir, csv_file_name) 
        print(f'Write to file: {csv_file}')
        make_dirs_for_file(path=csv_file)
        if not exist(path=csv_file, overwrite=True):
            with io.open(csv_file, 'wt', newline='') as file_object:
                fieldnames = [
                    'generation',
                    'min',
                    'max',
                    'mean',
                    'stdev',
                ]
                writer = DictWriter(file_object, fieldnames=fieldnames, dialect='excel')
                writer.writeheader()
                for csv_row in csv_data:
                    writer.writerow(csv_row)
                    
    return (best_solution, best_cost, csv_file)
        

    