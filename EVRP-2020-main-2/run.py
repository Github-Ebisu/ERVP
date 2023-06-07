# -*- coding: utf-8 -*-

import os
import argparse


from evrp.evrp_instance import EvrpInstance
from evrp.utils import *
from evrp.ga import run_GA

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname('.')))

DATA_DIR = os.path.join(BASE_DIR, 'evrp-benchmark-set')
RESULT_DIR = "D:\\EVRP_Final\\EVRP-2020-main\\results"


def main():
    instance_name = "E-n23-k3.evrp"
    seed = 42
    pop_size = 10000
    n_gen = 100
    cx_prob = 0.85
    mut_prob = 0.1
    indpb = 0.75


    file_dir = os.path.join(DATA_DIR, instance_name)
    instance = EvrpInstance(file_dir)

    best_solution, best_cost, training_file = run_GA(instance, seed, pop_size, n_gen, cx_prob, mut_prob, indpb, RESULT_DIR)

    df = create_dataframe(instance)


    print(f'Excepted optimum: {instance.optimum}')
    print(f'The optimal result cost from my GA: {best_cost}')
    print(best_solution)

    visualize(training_file)
    visualize_routes(best_solution, df, 'Best Solution for ' + instance.name)


def visualize(training_file):
    df_run = pd.read_csv(training_file)
    title = os.path.basename(training_file).split('_')[0] + ' GA '
    plot_training_graph(df_run, title)


if __name__ == '__main__':
    main()
    # visualize("/Users/yhq/Desktop/Code/EVRP-2020/results/E-n22-k4_seed1_nG200.csv")
    
