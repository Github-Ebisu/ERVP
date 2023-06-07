from evrp.utils import *
from evrp.evrp_instance import EvrpInstance

instance_name = "E-n33-k4.evrp"

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname('.')))
DATA_DIR = os.path.join(BASE_DIR, 'evrp-benchmark-set')
RESULT_DIR = os.path.join(BASE_DIR, 'results')
print(RESULT_DIR )
file_dir = os.path.join(DATA_DIR, instance_name)
instance = EvrpInstance(file_dir)

df = create_dataframe(instance)

save_path = os.path.join(RESULT_DIR, f'{instance.name}.png')
plot_nodes(df, instance.name, "results")