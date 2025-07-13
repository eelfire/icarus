#%%
#!/usr/bin/env python
"""Plot results read from a result set
"""
import os
import argparse
import logging

import numpy as np
import matplotlib.pyplot as plt
import scienceplots

from icarus.util import Settings, config_logging
from icarus.results import plot_lines, plot_bar_chart
from icarus.registry import RESULTS_READER


# Logger object
logger = logging.getLogger("plot")

# These lines prevent insertion of Type 3 fonts in figures
# Publishers don't want them
plt.rcParams["ps.useafm"] = True
plt.rcParams["pdf.use14corefonts"] = True

# If True text is interpreted as LaTeX, e.g. underscore are interpreted as
# subscript. If False, text is interpreted literally
plt.rcParams["text.usetex"] = False

# Aspect ratio of the output figures
plt.rcParams["figure.figsize"] = 6,6

# Size of font in legends
LEGEND_SIZE = 16

# Line width in pixels
LINE_WIDTH = 1.5

# Plot
PLOT_EMPTY_GRAPHS = True

# This dict maps strategy names to the style of the line to be used in the plots
STRATEGY_STYLE = {
    "LCE": "b-o",
    "LCD": "g-D",
    "PROB_CACHE": "m-^",
    "NO_CACHE": "c-s",
    "EDGE":"r-v",
    "CL4M":"b--p",
    "RAND_BERNOULLI":"g-->",
    "NO_CACHE_DNSSEC":"r-<",
}

# This dict maps name of strategies to names to be displayed in the legend
STRATEGY_LEGEND = {
    "LCE": "nise",
    "LCD": "nise-lcd",
    "PROB_CACHE": "nise",
    "NO_CACHE": "dns",
    "EDGE":"nise-edge",
    "CL4M":"nise-cl4m",
    "RAND_BERNOULLI":"nise-rand-bernoulli",
    "NO_CACHE_DNSSEC":"dnssec",
}

# Color and hatch styles for bar charts of cache hit ratio and link load vs topology
# STRATEGY_BAR_COLOR = {
#     "LCE": "k",
#     "LCD": "0.4",
#     "PROB_CACHE": "0.5",
#     "NO_CACHE": "0.6",
#     "EDGE":"0.7",
#     "CL4M":"0.8",# STRATEGY_BAR_HATCH = {
#     "LCE": None,
#     "LCD": None,
#     "PROB_CACHE": None,
#     "NO_CACHE": None,
#     "EDGE": None,
#     "CL4M": None,
#     "RAND_BERNOULLI": None,
# }

STRATEGY_BAR_HATCH = {
    "LCE": "xxx",
    "LCD": "xxx",
    "PROB_CACHE": "xxx",
    "NO_CACHE": "\\\\",
    "EDGE": "\\",
    "CL4M": "O",
    "RAND_BERNOULLI": "|",
    "NO_CACHE_DNSSEC":"///",
}

STRATEGY_BAR_COLOR = {
    "LCE": "#55a868",  # Green
    "LCD": "#ff9f4a",  # Orange
    "PROB_CACHE": "#c44e52",  # Red
    "NO_CACHE": "#4c72b0",  # Blue
    "EDGE": "#ccb974",  # Gold
    "CL4M": "#64b5cd",  # Cyan
    "RAND_BERNOULLI": "#8c8c8c",  # Gray
    "NO_CACHE_DNSSEC":"#ff69b4",  # Pink
}
STRATEGY_HATCH_COLOR = {
    "LCE":  (196/255, 78/255, 82/255),        # Green
    "LCD": (255/255, 159/255, 74/255),        # Orange
    "PROB_CACHE": (196/255, 78/255, 82/255),  # Red
    "NO_CACHE": (76/255, 114/255, 176/255),   # Blue
    "EDGE": (204/255, 185/255, 116/255),      # Gold
    "CL4M": (100/255, 181/255, 205/255),      # Cyan
    "RAND_BERNOULLI": (140/255, 140/255, 140/255),  # Gray
    "NO_CACHE_DNSSEC": (255/255, 105/255, 180/255), # Pink
}

#%%
def plot_latency_vs_alpha(resultset, cache_size, alpha_range, strategies, policy, plotdir):
    logger.info(f"Plotting latency vs alpha with cache size {cache_size} for policy {policy}")
    # if "NO_CACHE" in strategies:
    #     strategies = strategies.copy()
    #     strategies.remove("NO_CACHE")
    desc = {}
    # desc["title"] = "Latency: network cache size %={}".format(cache_size)
    desc["xlabel"] = "Content Distribution ($\\alpha$)"
    desc["ylabel"] = "Latency (ms)"
    desc["xparam"] = ("workload", "alpha")
    desc["xvals"] = alpha_range
    desc["filter"] = {"cache_placement": {"network_cache": cache_size}}
    desc["ymetrics"] = [("DNS_LATENCY", "MEAN")] * len(strategies)
    desc["ycondnames"] = [("strategy", "name")] * len(strategies)
    desc["ycondvals"] = strategies
    desc["errorbar"] = True
    desc["legend_loc"] = "upper right"
    desc["bar_color"] = STRATEGY_BAR_COLOR
    desc["bar_hatch"] = STRATEGY_BAR_HATCH
    desc["hatch_color"] = STRATEGY_HATCH_COLOR
    desc["legend"] = STRATEGY_LEGEND
    desc["plotempty"] = PLOT_EMPTY_GRAPHS
    # plot_lines(resultset, desc, "LATENCY_C={}.pdf".format(cache_size), plotdir)
    plotdir = os.path.join(plotdir, policy)
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)
        logger.debug(f"Created directory: {plotdir}")
    logger.debug(f"Plot directory: {plotdir}")
    plot_bar_chart(resultset, desc, "LATENCY_C={}.pdf".format(cache_size), plotdir)
    logger.debug(f"Saved latency plot for cache size {cache_size}")

#%%

def plot_cache_hits_vs_alpha(
    resultset, cache_size, alpha_range, strategies, policy, plotdir
):
    """
    Plot bar graphs of cache hit ratio for specific values of alpha and cache
    size for various topologies.

    The objective here is to show that our algorithms works well on all
    topologies considered
    """
    logger.info(f"Plotting cache hits vs alpha with cache size {cache_size} for policy {policy}")
    logger.debug(f"Using strategies: {strategies}")
    desc = {}
    # desc["title"] = "Cache Hit Ratio: network cache size %={}".format(cache_size)
    desc["xlabel"] = "Content Distribution ($\\alpha$)"
    desc["ylabel"] = "Cache Hit Ratio"
    desc["xparam"] = ("workload", "alpha")
    desc["xvals"] = alpha_range
    desc["filter"] = {
        "cache_placement": {"network_cache": cache_size},
    }
    desc["ymetrics"] = [("CACHE_HIT_RATIO", "MEAN")] * len(strategies)
    desc["ycondnames"] = [("strategy", "name")] * len(strategies)
    desc["ycondvals"] = strategies
    desc["errorbar"] = True
    desc["legend_loc"] = "upper right"
    desc["bar_color"] = STRATEGY_BAR_COLOR
    desc["bar_hatch"] = STRATEGY_BAR_HATCH
    desc["hatch_color"] = STRATEGY_HATCH_COLOR
    desc["legend"] = STRATEGY_LEGEND
    desc["plotempty"] = PLOT_EMPTY_GRAPHS

    plotdir = os.path.join(plotdir, policy)
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)
        logger.debug(f"Created directory: {plotdir}")
    
    output_file = "CACHE_HIT_RATIO__C={}.pdf".format(cache_size)
    logger.debug(f"Creating plot in {os.path.join(plotdir, output_file)}")
    plot_bar_chart(
        resultset,
        desc,
        output_file,
        plotdir,
    )
    logger.debug(f"Saved cache hit ratio plot for cache size {cache_size}")
#%%
def plot_hops_vs_alpha(
    resultset, cache_size, alpha_range, strategies, policy, plotdir
):
    """
    Plot bar graphs of cache hit ratio for specific values of alpha and cache
    size for various topologies.

    The objective here is to show that our algorithms works well on all
    topologies considered
    """
    desc = {}
    # desc["title"] = "Total Hops Per Resolution: network cache size %={}".format(cache_size*100)
    desc["xlabel"] = "Content Distribution ($\\alpha$)"
    desc["ylabel"] = "Mean Hops"
    desc["xparam"] = ("workload", "alpha")
    desc["xvals"] = alpha_range
    desc["filter"] = {
        "cache_placement": {"network_cache": cache_size},
    }
    desc["ymetrics"] = [("DNS_HOPS", "MEAN_HOPS")] * len(strategies)
    desc["ycondnames"] = [("strategy", "name")] * len(strategies)
    desc["ycondvals"] = strategies
    desc["errorbar"] = True
    desc["legend_loc"] = "upper right"
    desc["bar_color"] = STRATEGY_BAR_COLOR
    desc["bar_hatch"] = STRATEGY_BAR_HATCH
    desc["hatch_color"] = STRATEGY_HATCH_COLOR
    desc["legend"] = STRATEGY_LEGEND
    desc["plotempty"] = PLOT_EMPTY_GRAPHS

    plotdir = os.path.join(plotdir, policy)
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)
        logger.debug(f"Created directory: {plotdir}")

    plot_bar_chart(
        resultset,
        desc,
        "TOTAL_HOPS_C={}.pdf".format(cache_size),
        plotdir,
    )

#%%
# def plot_hops_vs_alpha(
#     resultset, cache_size, alpha_range, strategies, policy, plotdir
# ):
#     logger.info(f"Plotting total hops vs alpha with cache size {cache_size} for policy {policy}")
#     logger.debug(f"Using strategies: {strategies}")
#     """Custom function to plot network load with different weights by strategy"""
#     import numpy as np
#     import matplotlib.pyplot as plt
#     import scienceplots

# # with plt.style.context(["science",  "no-latex"]):
#     # Create figure and axis
#     fig, ax = plt.subplots(figsize=(8, 5))
#     # plt.rcParams["figure.figsize"] = 8, 5
#     # Set width of bars
#     bar_width = 0.15
#     index = np.arange(len(alpha_range))
    
#     # For each strategy, calculate and plot network load
#     for i, strategy in enumerate(strategies):
#         total_hopss = []
#         logger.debug(f"Processing strategy: {strategy}")
        
#         for alpha in alpha_range:
#             # Get relevant metrics for this combination
#             req_metric = 0
#             content_metric = 0
            
#             for result in resultset:
#                 # Extract configuration and metrics safely
#                 config = result[0] if isinstance(result[0], dict) else {}
#                 metrics = result[1] if len(result) > 1 else {}
                
#                 # Check if this result matches our criteria
#                 strategy_match = config.get('strategy', {}).get('name') == strategy
#                 cache_match = config.get('cache_placement', {}).get('network_cache') == cache_size
#                 alpha_match = config.get('workload', {}).get('alpha') == alpha
                
#                 if strategy_match and cache_match and alpha_match:
#                     # Found matching result, extract metrics
#                     req_metric = metrics.get('DNS_HOPS', {}).get('MEAN_HOPS', 0)
#                     content_metric = metrics.get('DNS_HOPS', {}).get('MEAN_HOPS', 0)
#                     break
            
#             # Set content weight based on strategy
#             if strategy == "NO_CACHE":
#                 # network_load = (req_metric*3 * 35) + (content_metric*3 * 143)
#                 total_hops = (req_metric * 3) + (content_metric * 3)
#                 # total_hops = metrics.get('DNS_HOPS', {}).get('TOTAL_HOPS', 0)
#                 # print(f"[DEBUG] total_hops: {total_hops}, req_metric: {req_metric}, content_metric: {content_metric}, sessions: {metrics.get('DNS_HOPS', {}).get('SESSIONS', 0)}")
#                 raise ValueError("Debugging total hops calculation")
#             elif strategy == "NO_CACHE_DNSSEC":
#                 # network_load = (req_metric* * 35) + (content_metric * 143)
#                 total_hops = req_metric*8 + content_metric*8
#             else:
#                 # network_load = (req_metric * 35) + (content_metric * 1158)
#                 total_hops = req_metric + content_metric
            
#             logger.debug(f"Strategy: {strategy}, Alpha: {alpha}, Total Hops: {total_hops}")
#             total_hopss.append(total_hops)
        
#         # Plot bars for this strategy
#         positions = index + (i * bar_width)
#         ax.bar(positions, total_hopss, bar_width,
#             color=STRATEGY_BAR_COLOR[strategy],
#             hatch=STRATEGY_BAR_HATCH[strategy],
#             label=STRATEGY_LEGEND[strategy])
    
#     # Set labels and title
#     ax.set_xlabel("Content distribution ($\\alpha$)", fontsize=16)
#     ax.set_ylabel("Total Hops", fontsize=16)
#     ax.set_title(f"Total Hops: cache size %={cache_size}", fontsize=16)
#     ax.set_xticks(index + bar_width * (len(strategies) - 1) / 2)
#     ax.set_xticklabels(alpha_range)
#     ax.legend(loc="upper right", fontsize=12)
    
#     plotdir = os.path.join(plotdir, policy)
#     if not os.path.exists(plotdir):
#         os.makedirs(plotdir)
#         logger.debug(f"Created directory: {plotdir}")

#     # Save figure
#     output_file = os.path.join(plotdir, f"TOTAL_HOPS_C={cache_size}.pdf")
#     logger.debug(f"Saving total hops plot to {output_file}")
#     plt.tight_layout()
#     plt.savefig(output_file)
#     plt.close()
#     logger.debug(f"Saved total hops plot for cache size {cache_size}")
#%%

def plot_network_load_vs_alpha(
    resultset, cache_size, alpha_range, strategies, policy, plotdir
):
    logger.info(f"Plotting network load vs alpha with cache size {cache_size} for policy {policy}")
    logger.debug(f"Using strategies: {strategies}")
    
    #remove DNSSEC from strategies
    # if "NO_CACHE_DNSSEC" in strategies:
    #     strategies = strategies.copy()
    #     strategies.remove("NO_CACHE_DNSSEC")

    # with plt.style.context(["science",  "no-latex"]):

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(6, 6))
    plt.rc("font", family="Open Sans", size=20)
    # Set width of bars
    bar_width = 0.15
    index = np.arange(len(alpha_range))
    
    # For each strategy, calculate and plot network load
    for i, strategy in enumerate(strategies):
        network_loads = []
        logger.debug(f"Processing strategy: {strategy}")
        
        for alpha in alpha_range:
            req_metric = 0
            content_metric = 0
            
            for result in resultset:
                config = result[0] if isinstance(result[0], dict) else {}
                metrics = result[1] if len(result) > 1 else {}
                
                strategy_match = config.get('strategy', {}).get('name') == strategy
                cache_match = config.get('cache_placement', {}).get('network_cache') == cache_size
                alpha_match = config.get('workload', {}).get('alpha') == alpha
                
                if strategy_match and cache_match and alpha_match:
                    req_metric = metrics.get('DNS_HOPS', {}).get('MEAN_HOPS', 0)
                    content_metric = metrics.get('DNS_HOPS', {}).get('MEAN_HOPS', 0)
                    break
            
            # CONTENT SIZES ESTIMATED THROUGH EXPERIMENTS
            if strategy == "NO_CACHE":
                network_load = (req_metric*3 * 35) + (content_metric*3 * 143) 
            elif strategy == "NO_CACHE_DNSSEC":
                network_load = (req_metric*3 * 35) + (content_metric*3 * 143) + (req_metric*5 * 44) + (content_metric*5 * 589)
            else:
                network_load = (req_metric * 35) + (content_metric * 1158)
            
            logger.debug(f"Strategy: {strategy}, Alpha: {alpha}, Network Load: {network_load}, Request Hops: {req_metric}, Content Hops: {content_metric}")
            network_loads.append(network_load)
        
        # Plot bars for this strategy
        positions = index + (i * bar_width)
        bars = ax.bar(positions, network_loads, bar_width,
            color="white",
            hatch=STRATEGY_BAR_HATCH[strategy],
            label=STRATEGY_LEGEND[strategy])
        for bar_container in bars:
            hatch_color = STRATEGY_HATCH_COLOR[strategy]
            bar_container.set_edgecolor("black")
            # print(f"[DEBUG] Setting hatch color {hatch_color[yvals[l]]} for {yvals[l]}")
            bar_container._hatch_color = hatch_color
    
    # Set labels and title
    ax.set_xlabel("Content Distribution ($\\alpha$)", fontsize=20)
    ax.set_ylabel("Mean Network\nLoad (bytes)", fontsize=20)
    # ax.set_title(f"Network Load: network cache size %={cache_size}", fontsize=16)
    ax.set_xticks(index + bar_width * (len(strategies) - 1) / 2)
    ax.set_xticklabels(alpha_range)
    ax.legend(loc="upper right", fontsize=16)

    plotdir = os.path.join(plotdir, policy)
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)
        logger.debug(f"Created directory: {plotdir}")
        
    # Save figure
    output_file = os.path.join(plotdir, f"NETWORK_LOAD_C={cache_size}.pdf")
    logger.debug(f"Saving network load plot to {output_file}")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    logger.debug(f"Saved network load plot for cache size {cache_size}")
#%%
def run(config, results, plotdir):
    """Run the plot script

    Parameters
    ----------
    config : str
        The path of the configuration file
    results : str
        The file storing the experiment results
    plotdir : str
        The directory into which graphs will be saved
    """
    settings = Settings()
    settings.read_from(config)
    logger.info(f"Loaded configuration from {config}")
    config_logging(settings.LOG_LEVEL)
    logger.info(f"Configured logging with level {settings.LOG_LEVEL}")
    
    resultset = RESULTS_READER[settings.RESULTS_FORMAT](results)
    logger.info(f"Loaded resultset using format {settings.RESULTS_FORMAT}")
    logger.debug(f"Result set size: {len(resultset)} entries")
    logger.debug(f"Data collectors: {settings.DATA_COLLECTORS}")
    
    # Create dir if not existsing
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)
        logger.debug(f"Created plot directory: {plotdir}")
    
    # Parse params from settings
    cache_sizes = settings.NETWORK_CACHE
    alphas = settings.ALPHA
    strategies = settings.STRATEGIES
    policies = settings.CACHE_POLICIES
    logger.debug(f"strategies = {strategies}")
    logger.debug(f"policies = {policies}")

    # collectors = settings.DATA_COLLECTORS
    
    # Plot graphs
    logger.debug(f"cache_sizes = {cache_sizes}")
    for policy in policies:
        logger.info("Plotting graphs for cache policy %s" % policy)
        for cache_size in cache_sizes:
            logger.info("Plotting latency for cache size %s vs alpha" % str(cache_size))
            plot_latency_vs_alpha(resultset, cache_size, alphas, strategies, policy, plotdir)
            logger.info("Plotting cache hit ratio for cache size %s vs alpha" % str(cache_size))
            plot_cache_hits_vs_alpha(resultset, cache_size, alphas, strategies, policy, plotdir)
            logger.info("Plotting total hops for cache size %s vs alpha" % str(cache_size))
            plot_hops_vs_alpha(resultset, cache_size, alphas, strategies, policy, plotdir)
            logger.info("Plotting network load for cache size %s vs alpha" % str(cache_size))
            plot_network_load_vs_alpha(resultset, cache_size, alphas, strategies, policy, plotdir)



        # plot cache hit ratio vs alpha

    logger.info("Exit. Plots were saved in directory %s" % os.path.abspath(plotdir))
#%%

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        "-r", "--results", dest="results", help="the results file", required=True
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        help="the output directory where plots will be saved",
        required=True
    )
    parser.add_argument("config", help="the configuration file")
    args = parser.parse_args()
    run(args.config, args.results, args.output)

#%%

if __name__ == "__main__":
    main()

#%%
# run("/home/mithilpn/Projects/project-course-dns/icarus/examples/dnsr/final/config.py",
#     "/home/mithilpn/Projects/project-course-dns/icarus/examples/dnsr/final/socc_final/results_garr.pkl",
#     "/home/mithilpn/Projects/project-course-dns/icarus/examples/dnsr/final/socc_final/garr")
#%%