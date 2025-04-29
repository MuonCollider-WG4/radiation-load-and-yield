#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import sys
from typing import Callable

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
# The tics shouls be inside the plot for both x and y
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
# Add subtics like root
plt.rcParams['xtick.minor.visible'] = True
plt.rcParams['ytick.minor.visible'] = True
# The grid should be dashed and grey and on by default
plt.rcParams['grid.color'] = 'grey'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.linewidth'] = 1
plt.rcParams['grid.alpha'] = 0.5
plt.rcParams['axes.grid'] = True
class Cycle:
    """
    Represents a cycle of a fluka simulation.

    Attributes:
        path (str): The path to the data file.
        df (pandas.DataFrame): The DataFrame containing the data.
    """
    def __init__(self, path : str):
        self.path = path
        self.df = pd.read_csv(path, 
                              skiprows=1, 
                              names=['id', 'kinE', 'x', 'y', 'z', 'cx', 'cy', 'cz'],
                              sep = r'\s+')

class Case:
    """
    Represents a case in the emittance calculator.
    
    Attributes:
        name (str): The name of the case.
        inputs (list): The input paths for the case.
        normalization (str): The normalization method for the case.
        label (str): The label for the case.
        cycles (list): The list of cycles for the case.
    """
    def __init__(self, name : str, options : dict):
        self.name = name
        self.inputs = options.get("inputs", [])
        if not self.inputs:
            print(f"Warning: 'inputs' missing for case {name}")
        self.normalization = options.get("normalization", "")
        if not self.normalization:
            print(f"Warning: 'normalization' missing for case {name}")
        self.label = options.get("label", "")
        if not self.label:
            print(f"Warning: 'label' missing for case {name}")
        self.cycles = [Cycle(path) for path in self.inputs]
        self.nprimary = options.get("nprimary", 0)
        if not self.nprimary:
            print(f"Warning: 'nprimary' missing for case {name}")

def _add_histogram_single_cycle(x_bins : np.array, 
                               cycle : Cycle, 
                               func_df : Callable[[pd.DataFrame], np.array], 
                               condition : str = '', 
                               normalization = 1,
                               weight_fun : Callable[[pd.DataFrame], np.array] = lambda x: np.ones(len(x))) -> tuple:
   df = cycle.df
   if condition != '':
      df = df.query(condition)
   counts, bins = np.histogram(func_df(df), 
                               bins = x_bins,
                               weights = weight_fun(df))
   return counts * normalization, counts * normalization

def get_histogram(x_bins : np.array, 
                  cycle_list : list[Cycle], 
                  func_df : Callable[[pd.DataFrame], np.array], 
                  condition : str = '', 
                  normalization = 1,
                  weight_fun : Callable[[pd.DataFrame], np.array] = lambda x: np.ones(len(x))) -> tuple:
    '''
    Function to add a histogram
    ----------
    Parameters:
        x_bins: bins of the histogram
        cycle: cycle to consider
        function: function to apply to the dataframe
        condition: condition to apply to the dataframe
        normalization: normalization of the histogram
        weight_fun: function to apply to the dataframe to get the weight
    Returns:
        counts: np.array
            counts of the histogram
        error: np.array
            error of the histogram (equal to counts!!)
    '''
        # Check the inputs
    if len(cycle_list) == 0:
        raise ValueError("Empty cycle list")
    if len(x_bins) == 0:
        raise ValueError("Empty x_bins")
    # If there is only one cycle, return the histogram, no need to batch analysis
    if len(cycle_list) == 1:
        return _add_histogram_single_cycle(x_bins, cycle_list[0], func_df, condition, normalization, weight_fun)
    # If there are more cycles, run a batch analysis
    tot_counts = np.zeros((len(cycle_list), len(x_bins) - 1))
    for num_cycle, cycle in enumerate(cycle_list):
        df = cycle.df
        if condition != '':
            df = df.query(condition)
        current_counts, bins = np.histogram(func_df(df), 
                                            bins = x_bins,
                                            weights = weight_fun(df))
        tot_counts[num_cycle, :] = current_counts
    counts = np.mean(tot_counts, axis = 0) * normalization
    error = np.std(tot_counts, axis = 0) / np.sqrt((len(cycle_list) - 1)) * normalization
    return counts, error

import numpy as np

def rmsEmittance(x, x_prime, y, y_prime):
    """
    Calculate the root mean square (RMS) emittance using the given phase space coordinates.

    Parameters:
    x (array-like): Array of x coordinates.
    x_prime (array-like): Array of x' (x prime) coordinates.
    y (array-like): Array of y coordinates.
    y_prime (array-like): Array of y' (y prime) coordinates.

    Returns:
    float: The calculated RMS emittance.

    Raises:
    None
    """
    matrix = np.vstack((x, x_prime, y, y_prime))
    covariance = np.cov(matrix)
    determinant = np.linalg.det(covariance)
    emittance = determinant**(1/4)
    if emittance == 0: return float('nan')
    return emittance

def get_emittance_hist(ene_bins : np.array, df : pd.DataFrame) -> np.array:
    """
    Calculate the emittance histogram for a given energy bin and dataframe.

    Parameters:
    ene_bins (array-like): Energy bins for grouping the data.
    df (pandas.DataFrame): Dataframe containing the kinematic and position data.

    Returns:
    array-like: Emittance values for each energy bin.

    """
    y_out = np.zeros(len(ene_bins) - 1)
    idx = 0
    for kin_en, group in df.groupby(pd.cut(df.kinE, ene_bins), observed=True):
        emittance = rmsEmittance(group.x * 1E-2, group.cx / group.cz, 
                                 group.y * 1E-2, group.cy / group.cz)
        y_out[idx] = emittance
        idx += 1        
    return y_out

def get_emittance_cycles(ene_bins : np.array,
                cycle_list : list[Cycle],
                condition : str = '', 
                normalization = 1,
                weight_fun : Callable[[pd.DataFrame], np.array] = lambda x: np.ones(len(x))) -> tuple:
    """
    Calculate the emittance for each energy bin over multiple cycles.

    Args:
        ene_bins (array-like): Energy bins.
        cycle_list (list): List of cycles.
        condition (str, optional): Condition to filter the data. Defaults to ''.
        normalization (float, optional): Normalization factor. Defaults to 1.
        weight_fun (Callable[[pd.DataFrame], np.array], optional): Function to calculate weights. Defaults to lambda x: np.ones(len(x)).

    Returns:
        tuple: A tuple containing the counts and error arrays.
    """
    tot_counts = np.zeros((len(cycle_list), len(x_bins) - 1))
    for num_cycle, cycle in enumerate(cycle_list):
        df = cycle.df
        if condition != '':
            df = df.query(condition)
        current_counts = get_emittance_hist(ene_bins, df)
        tot_counts[num_cycle, :] = current_counts
    counts = np.mean(tot_counts, axis = 0) * normalization
    error = np.std(tot_counts, axis = 0) / np.sqrt((len(cycle_list) - 1)) * normalization
    return counts, error
    


# Read json file to load all the options for each simulation case
json_path = "./inputfile_filled.json"
json_data = json.load(open(json_path, 'r'))
list_cases = [Case(name, options) for name, options in json_data.items()]
        
# For each case, get the histogram of the kinetic energy
x_bins = np.logspace(-2, 1, 100)
logdiff = np.diff(np.log(x_bins))
x_centre = x_bins[:-1] * np.exp(logdiff / 2)
fig, ax = plt.subplots(figsize=(5,2.8))
for case in list_cases:
    query = 'id == 10'
    counts, error = get_histogram(x_bins, case.cycles, lambda x: x.kinE, condition=query, normalization = 1/case.nprimary)
    ax.errorbar(x_centre, counts, yerr = error, label = case.label, fmt = ' ', capsize = 2)
ax.set_xscale('log')
ax.set_xlabel('Kinetic energy [GeV]')
ax.set_ylabel('E*dN/dE [-]')
ax.legend()
fig.savefig('kinetic_energy.png', dpi = 300, bbox_inches = 'tight')

fig, ax = plt.subplots(figsize=(5,2.8))
# Calculate the emittance for different kinetic energies
x_bins = np.linspace(0, 1, 20)
x_centre = x_bins[:-1] + np.diff(x_bins) / 2
x_err = np.diff(x_bins) / 2
for case in list_cases:
    query = 'id == 10'
    counts, error = get_emittance_cycles(x_bins, case.cycles, condition=query)
    ax.errorbar(x_centre, counts, xerr = x_err, yerr = error, label = case.label, fmt = ' ', capsize = 2)
ax.set_xlabel('Kinetic energy [GeV]')
ax.set_ylabel('Emittance [m rad]')
ax.legend()
ax.set_title('Emittance of muons plus')
fig.savefig('emittance.png', dpi = 300, bbox_inches = 'tight')

# %%
# Get the total counts for 10 and 11, and print it (muon and antimuon) all results are given per muon
def get_total_counts(cycle_list : list[Cycle], condition : str = '') -> tuple:
    """
    Calculate the total counts for a given condition.

    Parameters:
    cycle_list (list): List of cycles.
    condition (str, optional): Condition to filter the data. Defaults to ''.

    Returns:
    tuple: A tuple containing the counts and error arrays.
    """
    tot_counts = np.zeros(len(cycle_list))
    for num_cycle, cycle in enumerate(cycle_list):
        df = cycle.df
        if condition != '':
            df = df.query(condition)
        tot_counts[num_cycle] = len(df)
    counts = np.mean(tot_counts)
    error = np.std(tot_counts) / np.sqrt((len(cycle_list) - 1))
    return counts, error

for case in list_cases:
    query = 'id == 10'
    counts, error = get_total_counts(case.cycles, condition=query)
    counts /= case.nprimary
    error /= case.nprimary
    print(f"Case {case.label}: {counts:.2f} +- {error:.2f} (id == 10)")

    query = 'id == 11'
    counts, error = get_total_counts(case.cycles, condition=query)
    counts /= case.nprimary
    error /= case.nprimary
    print(f"Case {case.label}: {counts:.2f} +- {error:.2f} (id == 11)")

