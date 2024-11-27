from multiprocessing import cpu_count
from collections import deque
import copy
from icarus.util import Tree
from icarus.registry import register_topology_factory
from icarus.registry import register_workload
from icarus.scenarios.topology import IcnTopology
import random
import networkx as nx
import fnss
import numpy as np

############################## GENERAL SETTINGS ##############################

# Level of logging output
# Available options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# If True, executes simulations in parallel using multiple processes
# to take advantage of multicore CPUs
PARALLEL_EXECUTION = True

# Number of processes used to run simulations in parallel.
# This option is ignored if PARALLEL_EXECUTION = False
N_PROCESSES = cpu_count()

# Format in which results are saved.
# Result readers and writers are located in module ./icarus/results/readwrite.py
# Currently only PICKLE is supported
RESULTS_FORMAT = "PICKLE"

# Number of times each experiment is replicated
# This is necessary for extracting confidence interval of selected metrics
N_REPLICATIONS = 1

# List of metrics to be measured in the experiments
# The implementation of data collectors are located in ./icarus/execution/collectors.py
# Remove collectors not needed
DATA_COLLECTORS = [
    "CACHE_HIT_RATIO",  # Measure cache hit ratio
    "LATENCY",  # Measure request and response latency (based on static link delays)
    "LINK_LOAD",  # Measure link loads
    "PATH_STRETCH",  # Measure path stretch
]


########################## EXPERIMENTS CONFIGURATION ##########################

# Default experiment values, i.e. values shared by all experiments

# Number of content objects
N_CONTENTS = 3 * 10**5

# Number of content requests generated to pre-populate the caches
# These requests are not logged
N_WARMUP_REQUESTS = 0

# Number of content requests that are measured after warmup
N_MEASURED_REQUESTS = 6 * 10**5

# Number of requests per second (over the whole network)
REQ_RATE = 10.0

# Cache eviction policy
CACHE_POLICY = "LRU"

# Zipf alpha parameter, remove parameters not needed
# ALPHA = [0.6, 0.8, 1.0]
ALPHA = [0.6]

# Total size of network cache as a fraction of content population
# Remove sizes not needed
# NETWORK_CACHE = [0.004, 0.002]
NETWORK_CACHE = [0.004]


# List of topologies tested
# Topology implementations are located in ./icarus/scenarios/topology.py
# Remove topologies not needed
# TOPOLOGIES = [
#     "GEANT",
#     "WIDE",
#     "GARR",
#     "TISCALI",
# ]


# import pdb

# pdb.set_trace()


# print available topologies from the registry
from icarus.registry import TOPOLOGY_FACTORY

# DNS-specific topology parameters
# DNS_TOPOLOGY = {
#     "ROOT_SERVERS": 13,  # Number of root servers
#     "TLD_SERVERS": 50,  # Number of TLD servers
#     "AUTH_SERVERS": 100,  # Number of authoritative servers
#     "RESOLVERS": 30,  # Number of recursive resolvers
#     "CLIENTS": 1000,  # Number of clients
#     "ROUTERS": 1000,  # Number of routers
# }
DNS_TOPOLOGY = {
    "ROOT_SERVERS": 3,  # Number of root servers
    "TLD_SERVERS": 5,  # Number of TLD servers
    "AUTH_SERVERS": 10,  # Number of authoritative servers
    "RESOLVERS": 30,  # Number of recursive resolvers
    "CLIENTS": 100,  # Number of clients
    "ROUTERS": 50,  # Number of routers
}

"""
To create a custom topology, create a function returning an instance of the
`IcnTopology` class. An IcnTopology is simply a subclass of a Topology class
provided by FNSS.

A valid ICN topology must have the following attributes:
 * Each node must have one stack among: source, receiver, router
 * The topology must have an attribute called `icr_candidates` which is a set
   of router nodes on which a cache may be possibly deployed. Caches are not
   deployed directly at topology creation, instead they are deployed by a
   cache placement algorithm.
"""


# @register_topology_factory("TREE")
# def topology_tree(k, h, delay=1, **kwargs):
#     """Returns a tree topology, with a source at the root, receivers at the
#     leafs and caches at all intermediate nodes.

#     Parameters
#     ----------
#     h : int
#         The height of the tree
#     k : int
#         The branching factor of the tree
#     delay : float
#         The link delay in milliseconds

#     Returns
#     -------
#     topology : IcnTopology
#         The topology object
#     """
#     topology = fnss.k_ary_tree_topology(k, h)
#     receivers = [v for v in topology.nodes() if topology.node[v]["depth"] == h]
#     sources = [v for v in topology.nodes() if topology.node[v]["depth"] == 0]
#     routers = [v for v in topology.nodes() if topology.node[v]["depth"] > 0 and topology.node[v]["depth"] < h]
#     topology.graph["icr_candidates"] = set(routers)
#     for v in sources:
#         fnss.add_stack(topology, v, "source")
#     for v in receivers:
#         fnss.add_stack(topology, v, "receiver")
#     for v in routers:
#         fnss.add_stack(topology, v, "router")
#     # set weights and delays on all links
#     fnss.set_weights_constant(topology, 1.0)
#     fnss.set_delays_constant(topology, delay, "ms")
#     # label links as internal
#     for u, v in topology.edges():
#         topology.adj[u][v]["type"] = "internal"
#     return IcnTopology(topology)


# @register_topology_factory("DNS_HIERARCHY")
# def dns_hierarchy(rs, tld, auth, resolvers, clients, routers, **kwargs):
#     """
#     Create a DNS hierarchy topology
#     """
#     # Create a directed graph
#     topology = nx.DiGraph()
#     # Create a list of nodes
#     nodes = list(range(rs + tld + auth + resolvers + clients + routers))
#     # Add nodes to the graph
#     topology.add_nodes_from(nodes)
#     # Add edges to the graph
#     # Root servers are connected to TLD servers
#     for i in range(rs):
#         for j in range(tld):
#             topology.add_edge(i, rs + j)
#     # TLD servers are connected to authoritative servers
#     for i in range(tld):
#         for j in range(auth):
#             topology.add_edge(rs + i, rs + tld + j)
#     # Authoritative servers are connected to resolvers
#     for i in range(auth):
#         for j in range(resolvers):
#             topology.add_edge(rs + tld + i, rs + tld + auth + j)
#     # Resolvers are connected to clients
#     for i in range(resolvers):
#         for j in range(clients):
#             topology.add_edge(rs + tld + auth + i, rs + tld + auth + resolvers + j)
#     # Resolvers are connected to routers
#     for i in range(resolvers):
#         for j in range(routers):
#             topology.add_edge(rs + tld + auth + i, rs + tld + auth + resolvers + clients + j)
#     # Clients are connected to routers
#     for i in range(clients):
#         for j in range(routers):
#             topology.add_edge(rs + tld + auth + resolvers + i, rs + tld + auth + resolvers + clients + j)
#     # Set the root servers
#     root_servers = list(range(rs))
#     # Set the TLD servers
#     tld_servers = list(range(rs, rs + tld))
#     # Set the authoritative servers
#     auth_servers = list(range(rs + tld, rs + tld + auth))
#     # Set the resolvers
#     resolvers = list(range(rs + tld + auth, rs + tld + auth + resolvers))
#     # Set the clients
#     clients = list(range(rs + tld + auth + resolvers, rs + tld + auth + resolvers + clients))
#     # Set the routers
#     routers = list(range(rs + tld + auth + resolvers + clients, rs + tld + auth + resolvers + clients + routers))
#     # Set the stack of each node
#     for node in root_servers:
#         topology.node[node]["stack"] = "root_server"
#     for node in tld_servers:
#         topology.node[node]["stack"] = "tld_server"
#     for node in auth_servers:
#         topology.node[node]["stack"] = "auth_server"
#     for node in resolvers:
#         topology.node[node]["stack"] = "resolver"
#     for node in clients:
#         topology.node[node]["stack"] = "client"
#     for node in routers:
#         topology.node[node]["stack"] = "router"

#     # Set the icr_candidates
#     topology.graph["icr_candidates"] = set(routers)

#     # Set the link delays
#     for u, v in topology.edges():
#         topology[u][v]["delay"] = 1

#     return IcnTopology(topology)


print(TOPOLOGY_FACTORY.keys())
# exit()

TOPOLOGIES = [
    # "GEANT",
    "DNS_HIERARCHY",
]

# List of caching and routing strategies
# The code is located in ./icarus/models/strategy/*.py
# Remove strategies not needed
STRATEGIES = [
    "LCE",  # Leave Copy Everywhere
    # "NO_CACHE",  # No caching, shortest-path routing
    # "HR_SYMM",  # Symmetric hash-routing
    # "HR_ASYMM",  # Asymmetric hash-routing
    # "HR_MULTICAST",  # Multicast hash-routing
    # "HR_HYBRID_AM",  # Hybrid Asymm-Multicast hash-routing
    # "HR_HYBRID_SM",  # Hybrid Symm-Multicast hash-routing
    # "CL4M",  # Cache less for more
    # "PROB_CACHE",  # ProbCache
    # "LCD",  # Leave Copy Down
    # "RAND_CHOICE",  # Random choice: cache in one random cache on path
    # "RAND_BERNOULLI",  # Random Bernoulli: cache randomly in caches on path
]

# Instantiate experiment queue
EXPERIMENT_QUEUE = deque()

# Build a default experiment configuration which is going to be used by all
# experiments of the campaign
default = Tree()

default["topology"] = {
    "name": "DNS_HIERARCHY",
    "rs": DNS_TOPOLOGY["ROOT_SERVERS"],
    "tld": DNS_TOPOLOGY["TLD_SERVERS"],
    "auth": DNS_TOPOLOGY["AUTH_SERVERS"],
    "resolvers": DNS_TOPOLOGY["RESOLVERS"],
    "clients": DNS_TOPOLOGY["CLIENTS"],
    "routers": DNS_TOPOLOGY["ROUTERS"],
}
default["workload"] = {
    "name": "STATIONARY",
    "n_contents": N_CONTENTS,
    "n_warmup": N_WARMUP_REQUESTS,
    "n_measured": N_MEASURED_REQUESTS,
    "rate": REQ_RATE,
}
default["cache_placement"]["name"] = "UNIFORM"
default["content_placement"]["name"] = "UNIFORM"
default["cache_policy"]["name"] = CACHE_POLICY

# Create experiments multiplexing all desired parameters
for alpha in ALPHA:
    for strategy in STRATEGIES:
        for topology in TOPOLOGIES:
            for network_cache in NETWORK_CACHE:
                experiment = copy.deepcopy(default)
                experiment["workload"]["alpha"] = alpha
                experiment["strategy"]["name"] = strategy
                experiment["topology"]["name"] = topology
                experiment["cache_placement"]["network_cache"] = network_cache
                experiment["desc"] = "Alpha: {}, strategy: {}, topology: {}, network cache: {}".format(
                    str(alpha),
                    strategy,
                    topology,
                    str(network_cache),
                )
                EXPERIMENT_QUEUE.append(experiment)
