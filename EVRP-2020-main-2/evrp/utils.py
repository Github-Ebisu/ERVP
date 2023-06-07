# -*- coding: utf-8 -*-
import os
import time
import pandas as pd


import matplotlib.pyplot as plt
import matplotlib.colors as mcolors



# ************************************************************************
# *********************** Feasibility Judgement **************************

def is_capacity_feasible(individual, capacity, demands):
    """Check if a given individual is feasible with respect to vehicle capacity.
    
    Args:
        individual: A list of lists, where each sublist represents a vehicle and its assigned customers.
        capacity: The capacity of the vehicles.
        demands: The dictionary containing the demands of each customer.
        
    Returns:
        bool: True if the individual is feasible, False otherwise.
    """
    
    if not individual:
        return False

    # Iterate through each route in the individual
    for route in individual:
        # Calculate the total demand of the customers in the route
        total_demand = sum(demands[f'{customer}'] for customer in route)
        
        # If the total demand exceeds the vehicle's capacity, the individual is not feasible
        if total_demand > capacity:
            return False
    
    # If none of the routes exceed the vehicle's capacity, the individual is feasible
    return True




# ************************************************************************
# ***************************** Auxiliary ********************************

def reconstruct_individual(flat_ind, route_lengths):
    '''Reconstruct the original format of an individual from a flattened version.
    
    Args:
        flat_ind: A flattened version of an individual, where all routes are combined into a single list.
        route_lengths: A list of integers representing the length of each route in the original individual format.

    Returns:
        A list of lists, where each sublist represents a vehicle and its assigned customers.
    '''
    individual = []
    start_idx = 0
    for length in route_lengths:
        individual.append(flat_ind[start_idx:start_idx + length])
        start_idx += length
    return individual


def deduplicate_population(population):
    """
    Remove duplicate individuals from a population.
    
    Args:
        population: A list of individuals.
        
    Returns:
        A deduplicated population as a list.
    """
    deduplicated_population = []

    for individual in population:
        if individual not in deduplicated_population:
            deduplicated_population.append(individual)

    return deduplicated_population

def find_nearest_station(node_no, distance_matrix, station_list):
    '''Find the nearest charging station of the given node
    
    Args:
        node: the index of the node
        distance_matrix: the distance matrix of nodes
        staion_list: the list of station nodes 
    
    Returns:
        the index of the station
    '''
    return int(min(station_list, key=lambda station_no: distance_matrix[int(node_no)][int(station_no)])) 


def fitness_evaluation(individual, distance_matrix):
    '''Evaluate the generated routes
    
    Args:
        individual: A list of routes. Each route is a list of nodes.
        instance: the benchmark instance got from the original data
        
    Returns:
        tuple - (float, ) single objective fitness, which is used to satisfy the requirement of `deap.creator` fitness
    '''    
    
    total_distance = 0.0
    
    for route in individual:
        _route = [0] + route + [0]
        for current in range(1, len(_route)):
            prev_node = _route[current - 1]
            cur_node  = _route[current]
            total_distance += distance_matrix[prev_node][cur_node]
    
    return total_distance



# ************************************************************************
# ******************************* Plot ***********************************

def create_dataframe(instance):
    '''Create a dataframe from the instance

    Args:
        instance: the Object obtained from the Benchmark Instance
    '''
    # Create an empty dataframe
    df = pd.DataFrame(columns=['node_no', 'x_pos', 'y_pos', 'label'], dtype=str)
    

    # Iterate through key-value pairs, unpacking the tuple in the loop
    for key, value in instance.node_coordinates.items():
        if key == instance.depot_index:
            new_row = pd.DataFrame({'node_no': [str(key)],
                                    'x_pos': [value[0]],
                                    'y_pos': [value[1]],
                                    'label': ['depot']
                                   })
            df = pd.concat([df, new_row], ignore_index=True)        
        elif key in instance.station_list:
            new_row = pd.DataFrame({'node_no': [str(key)],
                                    'x_pos': [value[0]],
                                    'y_pos': [value[1]],
                                    'label': ['station']
                                   })
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            new_row = pd.DataFrame({'node_no': [str(key)],
                                    'x_pos': [value[0]],
                                    'y_pos': [value[1]],
                                    'label': ['customer']
                                   })
            df = pd.concat([df, new_row], ignore_index=True)
    
    return df

def plot_nodes(df, title='Scatter Plot', is_save=True, save_path='D:\\EVRP_Final\\EVRP-2020-main\\results\\pictures'):
    '''Plot the instance from the benchmark

    Args:
        df: pandas dataframe, it contains "node_no	x_pos	y_pos	label" columns
        title: the title of the plot
        save_path: the save path of the plot
    '''
    colors = {'depot': 'red', 'customer': 'blue', 'station': 'black'}
    markers = {'depot': 'D', 'customer': 'o', 'station': 's'}
    
    file_name = f"{title}_plot.png"
    file_name = os.path.basename(file_name)
    save_path = os.path.join(save_path, file_name)

    fig, ax = plt.subplots(figsize=(12, 8))
    for label, group in df.groupby('label'):
        if label == 'depot':
            group.plot(kind='scatter', x='x_pos', y='y_pos', label=label, color=colors[label], marker=markers[label], ax=ax)
        else:
            group.plot(kind='scatter', x='x_pos', y='y_pos', label=label, color=colors[label], marker=markers[label], ax=ax)

        # Add node_no labels for customer nodes
        if label == 'customer':
            for index, row in group.iterrows():
                ax.text(row['x_pos'] + 1, row['y_pos'] - 1, str(row['node_no']), fontsize=10, color=colors[label])
        elif label == 'station':
            for index, row in group.iterrows():
                ax.text(row['x_pos'] + 1, row['y_pos'] + 1, str(row['node_no']), fontsize=10, color=colors[label])

    ax.set_title(title)
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')

    # Move the legend and show the plot inside the loop
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Save the plot to the specified path
    if is_save:
        plt.savefig(save_path, bbox_inches='tight')
    
    # Show the plot
    plt.show()

def plot_route(route, df, ax, route_color='green', linewidth=1):
    '''Plots a single route on a given Axes instance.

    Args:
        route: A list of nodes representing the route.
        df: A DataFrame with node details, with columns 'x_pos' and 'y_pos' for coordinates.
        ax: The Axes instance on which the route is to be plotted.
        route_color: The color to be used for the route. Defaults to 'green'.
        linewidth: The width of the line representing the route. Defaults to 1.
    '''
    # Add the depot index (0) at the beginning and end of the route
    route_with_depot = [0] + route + [0]

    for i in range(len(route_with_depot) - 1):
        start_customer_idx = route_with_depot[i]
        end_customer_idx = route_with_depot[i + 1]

        x1, y1 = df['x_pos'].loc[start_customer_idx], df['y_pos'].loc[start_customer_idx]
        x2, y2 = df['x_pos'].loc[end_customer_idx], df['y_pos'].loc[end_customer_idx]

        ax.plot([x1, x2], [y1, y2], color=route_color, linewidth=linewidth)

def visualize_routes(routes, df, title='Routes', is_show=True, is_save=True, save_path='D:\\EVRP_Final\\EVRP-2020-main\\results\\routes'):
    '''Visualizes all routes on a single plot.

    Args:
        routes: A list of routes, where each route is a list of nodes.
        df: A DataFrame with node details, with columns 'x_pos' and 'y_pos' for coordinates.
        title: The title of the plot. Defaults to 'Route Plot'.
        is_save: whether save the image.
        save_path: the save path.
    '''
    colors = {'depot': 'red', 'customer': 'blue', 'station': 'black'}
    markers = {'depot': 'D', 'customer': 'o', 'station': 's'}
    
    file_name = f"{title}_plot.png"
    file_name = os.path.basename(file_name)
    save_path = os.path.join(save_path, file_name)
    print(save_path, '============')

    fig, ax = plt.subplots(figsize=(12, 8))
    for label, group in df.groupby('label'):
        if label == 'depot':
            group.plot(kind='scatter', x='x_pos', y='y_pos', label=label, color=colors[label], marker=markers[label], ax=ax, s=30)
        elif label == 'customer':
            group.plot(kind='scatter', x='x_pos', y='y_pos', label=label, color=colors[label], marker=markers[label], ax=ax)
        else:  # For the 'station' label
            group.plot(kind='scatter', x='x_pos', y='y_pos', label=label, color=colors[label], marker=markers[label], ax=ax, s=30) 
            

        # Add node_no labels for customer nodes
        if label == 'customer':
            for index, row in group.iterrows():
                ax.text(row['x_pos'] + 1, row['y_pos'] - 1, str(row['node_no']), fontsize=10, color=colors[label])
        elif label == 'station':
            for index, row in group.iterrows():
                ax.text(row['x_pos'] + 1, row['y_pos'] + 1, str(row['node_no']), fontsize=10, color=colors[label])
    
    # Create a colormap and generate a list of colors for each route
    colormap = plt.cm.get_cmap('tab10', len(routes))
    colors = [mcolors.rgb2hex(colormap(i)[:3]) for i in range(len(routes))]

    for i, route in enumerate(routes):
        plot_route(route, df, ax, route_color=colors[i])
    
    
    ax.set_title(title)
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')

    # Move the legend and show the plot inside the loop
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    if is_save:
        plt.savefig(save_path, bbox_inches='tight')
    
    if is_show:
        plt.show()

def plot_training_graph(df, title, is_show=True, is_save=True, save_path='D:\\EVRP_Final\\EVRP-2020-main\\results\\tranning_img'):
    """Plot a line graph for mean and mean by generation using a DataFrame.
    It's used to visualize the training process.
    
    Args:
        df: A pandas DataFrame containing 'generation', 'mean', and 'mean' columns.
        title: the graph title.
        is_save: whether save the image.
        save_path: the save path.
    """
    file_name = f"{title}_plot.png"
    file_name = os.path.basename(file_name)
    save_path = os.path.join(save_path, file_name)
    
    # Set the figure size (width, height) in inches
    plt.figure(figsize=(12, 6))

    # Plot the line graph for mean
    plt.plot(df['generation'], df['mean'], label='Average Fitness')

    # Plot the line graph for mean
    plt.plot(df['generation'], df['min'], label='Minimum Fitness')

    plt.plot(df['generation'], df['max'], label='Maximum Fitness')

    # Set the labels for the X and Y axes
    plt.xlabel('Generation')
    plt.ylabel('Fitness')

    # Set the title for the graph
    plt.title(f'{title} Training Process')

    # Add a legend to the graph
    plt.legend()

    if is_save:
        plt.savefig(save_path)

    # Display the graph
    if is_show:
        plt.show()
 

class InfeasibleError(Exception):
    pass


# ************************************************************************
# ***************************** Save File ********************************

def make_dirs_for_file(path):
    '''Make directories for the file
    
    Args:
        path: the given file path
    '''
    try:
        os.makedirs(os.path.dirname(path))
    except OSError:
        pass

def guess_path_type(path):
    '''judge the type of the given path
    
    Args:
        path: the given file path
    '''
    if os.path.isfile(path):
        return 'File'
    if os.path.isdir(path):
        return 'Directory'
    if os.path.islink(path):
        return 'Symbolic Link'
    if os.path.ismount(path):
        return 'Mount Point'
    return 'Path'

def exist(path, overwrite=False, display_info=False):
    '''judge whether it exists for the given path
    
    Args:
        path: the given file path
        overwrite: whether overwrite the file
        display_info: whether display the info of the path
    '''
    if os.path.exists(path):
        if overwrite:
            if display_info:
                print(f'{guess_path_type(path)}: {path} exists. Overwrite.')
            os.remove(path)
            return False
        if display_info:
            print(f'{guess_path_type(path)}: {path} exists.')
        return True
    if display_info:
        print(f'{guess_path_type(path)}: {path} does not exist.')
    return False


# ************************************************************************
# ***************************** Statistics *******************************

