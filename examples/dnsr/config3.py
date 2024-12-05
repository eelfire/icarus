# Shared parameters
NUM_CONTENTS = 1000
CACHE_POLICY_DNSR = "LRU"
CACHE_SIZE_DNSR = 100
NUM_REQUESTS = 5000

# Topology-specific parameters
TOPOLOGY_SETTINGS = {
    "dns_hierarchy": {
        "cache": "NO_CACHE"
    },
    "dnsr": {
        "cache": CACHE_POLICY_DNSR,
        "cache_size": CACHE_SIZE_DNSR
    }
}
