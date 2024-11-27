"""Configuration file for DNS resolver simulation."""

from multiprocessing import cpu_count
from collections import deque
import copy
from icarus.util import Tree

# GENERAL SETTINGS
LOG_LEVEL = "INFO"
PARALLEL_EXECUTION = True
N_PROCESSES = cpu_count()
N_REPLICATIONS = 1

# DNS-specific collectors
DATA_COLLECTORS = [
    "CACHE_HIT_RATIO",
    "LATENCY",
    "LINK_LOAD",
    "DNS_QUERY_TYPE_RATIO",
    "DNS_RESOLUTION_PATH",
]

# DNS Record Types to simulate
DNS_RECORD_TYPES = ["A", "AAAA", "NS", "MX", "TXT", "CNAME"]

# DNS-specific topology parameters
DNS_TOPOLOGY = {
    "ROOT_SERVERS": 13,  # Number of root servers
    "TLD_SERVERS": 50,  # Number of TLD servers
    "AUTH_SERVERS": 100,  # Number of authoritative servers
    "RESOLVERS": 30,  # Number of recursive resolvers
    "CLIENTS": 1000,  # Number of clients
}

# DNS Workload parameters
N_DOMAINS = 10**5  # Number of unique domain names
N_WARMUP = 10**4  # Warmup queries
N_MEASURED = 10**5  # Measured queries
QUERY_RATE = 100.0  # Queries per second

# Cache parameters
RESOLVER_CACHE_SIZE = 0.01  # 1% of total domains
TTL_RANGES = {
    "ROOT": 518400,  # 6 days
    "TLD": 172800,  # 2 days
    "AUTH": 3600,  # 1 hour
}

# Create experiment queue
EXPERIMENT_QUEUE = deque()

# Base experiment configuration
default = Tree()

default["topology"] = {
    "name": "DNS_HIERARCHY",
    "root_servers": DNS_TOPOLOGY["ROOT_SERVERS"],
    "tld_servers": DNS_TOPOLOGY["TLD_SERVERS"],
    "auth_servers": DNS_TOPOLOGY["AUTH_SERVERS"],
    "resolvers": DNS_TOPOLOGY["RESOLVERS"],
    "clients": DNS_TOPOLOGY["CLIENTS"],
}

default["workload"] = {
    "name": "DNS_QUERY",
    "n_domains": N_DOMAINS,
    "n_warmup": N_WARMUP,
    "n_measured": N_MEASURED,
    "rate": QUERY_RATE,
    "record_types": DNS_RECORD_TYPES,
    "query_pattern": "ZIPF",
    "alpha": 0.8,  # Zipf parameter for domain popularity
}

default["cache_placement"] = {
    "name": "DNS_CACHE",
    "resolver_cache_size": RESOLVER_CACHE_SIZE,
    "ttl_ranges": TTL_RANGES,
}

default["content_placement"] = {"name": "DNS_ZONES", "zone_distribution": "UNIFORM"}

default["cache_policy"] = {
    "name": "TTL_LRU",  # TTL-aware LRU cache
}

# DNS resolution strategies to test
STRATEGIES = [
    "ITERATIVE",  # Resolver performs iterative queries
    "RECURSIVE",  # Resolver sends recursive queries
    "QNAME_MINIMIZATION",  # RFC 7816 QNAME minimization
    "AGGRESSIVE_NSEC",  # Aggressive use of NSEC/NSEC3
]

# Create experiments for each strategy
for strategy in STRATEGIES:
    experiment = copy.deepcopy(default)
    experiment["strategy"] = {
        "name": strategy,
    }
    experiment["desc"] = f"DNS Resolution Strategy: {strategy}"
    EXPERIMENT_QUEUE.append(experiment)
