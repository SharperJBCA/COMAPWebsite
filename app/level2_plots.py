import matplotlib.pyplot as plt
from astropy.time import Time
from datetime import datetime
import numpy as np 
import os
from .create_all import Level1File
import matplotlib.dates as mdates
from datetime import timedelta
import pandas as pd

# First, we want to organise the html pages, we want a page that lists all of the months, 
# that then lists all of the sources, and finally all of the plot types for that source. 

LEVEL2_DIR = '/scratch/nas_core/sharper/COMAP/level2_2023/'

def get_available_months():
    """Return a list of available months."""
    return sorted([folder for folder in os.listdir(LEVEL2_DIR) if os.path.isdir(os.path.join(LEVEL2_DIR, folder))])

def get_sources_for_month(month):
    """Return a list of sources for a given month."""
    month_dir = os.path.join(LEVEL2_DIR, month)
    return sorted([folder for folder in os.listdir(month_dir) if os.path.isdir(os.path.join(month_dir, folder))])

def get_observations_for_source(month, source):
    """Return a list of observation IDs for a given source and month."""
    source_dir = os.path.join(LEVEL2_DIR, month, source, "figures")
    return sorted([obs_id for obs_id in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, obs_id))])

def get_plots_for_observation(month, source, observation_id, prefixes):
    """Return a list of available plots for a given observation."""
    obs_dir = os.path.join(LEVEL2_DIR, month, source, "figures", observation_id)
    available_plots = []
    for prefix in prefixes:
        for file in os.listdir(obs_dir):
            if file.startswith(prefix):
                available_plots.append(file)
    return sorted(available_plots)
