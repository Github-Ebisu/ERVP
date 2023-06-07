# -*- coding: utf-8 -*-

import os
import argparse


from evrp.evrp_instance import EvrpInstance
from evrp.utils import *
from evrp.ga import run_GA

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname('.')))

DATA_DIR = os.path.join(BASE_DIR, 'evrp-benchmark-set')


def main():
    instance_name = "E-n23-k3.evrp"

    file_dir = os.path.join(DATA_DIR, instance_name)
    instance = EvrpInstance(file_dir)
    
    print(instance.capacity)
    print(instance.demands)
    print(instance.name)
    
main()