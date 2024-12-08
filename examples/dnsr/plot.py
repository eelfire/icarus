#!/usr/bin/env python
"""Plot results read from a result set
"""
import os
import argparse
import logging

import matplotlib.pyplot as plt

from icarus.util import Settings, config_logging
from icarus.results import plot_lines
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
plt.rcParams["figure.figsize"] = 8, 5

# Size of font in legends
LEGEND_SIZE = 14

# Line width in pixels
LINE_WIDTH = 1.5

# Plot
PLOT_EMPTY_GRAPHS = True

# This dict maps strategy names to the style of the line to be used in the plots
STRATEGY_STYLE = {
    "LCE": "b--p",
    "NO_CACHE": "k:o",
}

# This dict maps name of strategies to names to be displayed in the legend
STRATEGY_LEGEND = {
    "LCE": "dns-ndn",
    "NO_CACHE": "dns-hierarchial",
}

# Color and hatch styles for bar charts of cache hit ratio and link load vs topology
STRATEGY_BAR_COLOR = {
    "LCE": "k",
    "NO_CACHE": "0.5",
}

STRATEGY_BAR_HATCH = {
    "LCE": None,
    "NO_CACHE": "x",
}


def plot_latency_vs_alpha(resultset, cache_size, alpha_range, strategies, plotdir):
    # if "NO_CACHE" in strategies:
    #     strategies = strategies.copy()
    #     strategies.remove("NO_CACHE")
    desc = {}
    desc["title"] = "Latency: cache size %={}".format(cache_size*100)
    desc["xlabel"] = "Content distribution (alpha)"
    desc["ylabel"] = "Latency (ms)"
    desc["xparam"] = ("workload", "alpha")
    desc["xvals"] = alpha_range
    desc["filter"] = {"cache_placement": {"network_cache": cache_size}}
    desc["ymetrics"] = [("LATENCY", "MEAN")] * len(strategies)
    desc["ycondnames"] = [("strategy", "name")] * len(strategies)
    desc["ycondvals"] = strategies
    desc["errorbar"] = True
    desc["legend_loc"] = "upper right"
    desc["line_style"] = STRATEGY_STYLE
    desc["legend"] = STRATEGY_LEGEND
    desc["plotempty"] = PLOT_EMPTY_GRAPHS
    plot_lines(resultset, desc, "LATENCY_C={}.pdf".format(cache_size), plotdir)


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
    config_logging(settings.LOG_LEVEL)
    resultset = RESULTS_READER[settings.RESULTS_FORMAT](results)
    # Create dir if not existsing
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)
    # Parse params from settings
    cache_sizes = settings.NETWORK_CACHE
    alphas = settings.ALPHA
    strategies = settings.STRATEGIES
    # Plot graphs
    for cache_size in cache_sizes:
        logger.info("Plotting latency for cache size %s vs alpha" % str(cache_size))
        plot_latency_vs_alpha(resultset, cache_size, alphas, strategies, plotdir)
    logger.info("Exit. Plots were saved in directory %s" % os.path.abspath(plotdir))


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


if __name__ == "__main__":
    main()