import os
from icarus.results.visualize import draw_stack_deployment
# Assuming 'topo' is an instance of the Icarus Topology class
from icarus.registry import (
    TOPOLOGY_FACTORY,
)
import matplotlib.pyplot as plt
import networkx as nx

topo_spec = {'name': 'GARR_DNS'}
topology = TOPOLOGY_FACTORY["GARR_DNS"](**topo_spec)

output_dir = "/home/mithilpn/Projects/project-course-dns/icarus/examples/dnsr/final"
output_filename = "topo_test.png"

os.makedirs(output_dir, exist_ok=True)

plt.figure()
nx.draw_graphviz(topology, with_labels=False)
plt.savefig(os.path.join(output_dir, output_filename), bbox_inches="tight")

print(f"Stack deployment plot saved to {os.path.join(output_dir, output_filename)}")
