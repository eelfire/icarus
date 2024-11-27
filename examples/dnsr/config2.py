from multiprocessing import cpu_count
from collections import deque
import copy
from icarus.util import Tree

LOG_LEVEL = "INFO"
PARALLEL_EXECUTION = True
N_PROCESSES = cpu_count()
RESULTS_FORMAT = "PICKLE"
N_REPLICATIONS = 3

DATA_COLLECTORS = [
    # "CACHE_HIT_RATIO",
    "LATENCY",
    # "LINK_LOAD",
    # "PATH_STRETCH",
]

N_CONTENTS = 3 * 10**5
# N_WARMUP_REQUESTS = 3 * 10**5
N_WARMUP_REQUESTS = 0
N_MEASURED_REQUESTS = 6 * 10**5
REQ_RATE = 1.0
CACHE_POLICY = "LRU"
ALPHA = [0.6, 0.8, 1.0, 1.2]
NETWORK_CACHE = [0.004, 0.002]

TOPOLOGIES = [
    "GEANT",
    # "WIDE",
    # "GARR",
    "TISCALI",
]

STRATEGIES = [
    "LCE",  # Leave Copy Everywhere
    "NO_CACHE",  # No caching, shortest-path routing (Traditional DNS)
    "HR_HYBRID_SM",
]

EXPERIMENT_QUEUE = deque()

default = Tree()
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
