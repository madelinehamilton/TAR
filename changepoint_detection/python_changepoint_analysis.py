# Imports
import pandas as pd
import matplotlib.pylab as plt
import ruptures as rpt
import numpy as np
import os

"""
python_changepoint_analysis.py applies three different Python-based changepoint detection methods to the smoothed time
series using the ruptures library: the PELT, bottom-up, and window sliding methods. See
Truong et al. (2020) for a review of offline changepoint detection methods.

Inputs - .csv with the smoothed time series.
Outputs - (Saved) A .csv with changepoints from all methods

You need to specify the base directory.
"""

"""
DIRECTORIES
"""
# SPECIFY ROOT DIRECTORY
base_dir = "/Users/madelinehamilton/Documents/python_stuff/tar_repo/"
# Normalized time series
ts_dir = os.path.join(base_dir, "output_data/time_series/norm_time_series.csv")
# Desired directory of full changepoint table
cpt_table_name = os.path.join(base_dir, "output_data/changepoints/python_changepoints.csv")

"""
DATA PREPARATION
"""
# Read in the data, drop first and last two rows (N/A due to smoothing)
ts_norm = pd.read_csv(ts_dir).dropna()
# Drop the 'Year column'
ts_norm = ts_norm.drop('Year', axis=1)

"""
Parameter spaces for changepoint detection
"""
# Features to analyze
to_analyze = list(ts_norm.columns) + ['Multivariate']
# Cost functions
cost_functions = ["l1", "l2"]
# Minimum space between changepoints
minimum_gaps = [5, 6, 7, 8, 9, 10]
# Number of changepoints
num_cpts_vals = [False, 1, 2, 3, 4]
# For the sliding window method
window_sizes = [4, 6, 8, 10, 12, 14]
# Penalties
pen_values = list(np.linspace(0.2, 2, 5))

"""
ANALYSIS
"""

"""
Traverse through the parameter space and get the changepoints from each method
"""

all_info = []

"""
For each feature to analyze
"""
for var in to_analyze:
    # Get the correct feature data
    data = 0
    if var == 'Multivariate':
        # ndarray with all features
        data = np.array(ts_norm)
    else:
        data = np.array(ts_norm[var])

    """
    For each cost function {"l1", "l2"}
    """
    for cost in cost_functions:
        model = cost

        """
        For each changepoint gap {5, 6, 7, 8, 9, 10}
        """
        for gap in minimum_gaps:
            """
            PELT method: iterate through different penalty values
            """
            for pen in pen_values:
                algo = rpt.Pelt(model=model, min_size=gap).fit(data)
                cpts = algo.predict(pen=pen)
                # Store information: feature, method, cost function, number of cpts, minimum gap, penalty, window size, cpt value
                for cpt in cpts:
                    all_info.append([var, 'PELT', cost, 'N/A', gap, pen, 'N/A', cpt])

            """
            Bottom-up method: iterate through different numbers of changepoints {NULL, 1, 2, 3, 4}
            """
            for num in num_cpts_vals:
                algo = rpt.BottomUp(model=model, min_size=gap).fit(data)
                cpts = 0
                # If we know the number of breakpoints
                if num:
                    cpts = algo.predict(n_bkps=num)

                # If we don't specify a number of changepoints, we need to modify the penalty
                else:
                    n = len(data)
                    cpts = algo.predict(pen=np.log(n))

                # Store information
                for cpt in cpts:
                    all_info.append([var, 'Bottom-up', cost, num, gap, 'N/A', 'N/A', cpt])
        """
        Window method: iterate through window sizes {4, 6, 8, 10, 14} and numbers of changepoints {NULL, 1, 2, 3, 4}
        """
        for win in window_sizes:
            for num in num_cpts_vals:
                algo = rpt.Window(width=win, model=model).fit(data)
                cpts = 0

                # If we know the number of breakpoints
                if num:
                    cpts = algo.predict(n_bkps=num)

                # If we don't specify a number of changepoints, we need to modify the penalty
                else:
                    n = len(data)
                    cpts = algo.predict(pen=np.log(n))

                # Store information
                for cpt in cpts:
                    all_info.append([var, 'Window', cost, num, 'N/A', np.log(n), win, cpt])

"""
Compile data into a DataFrame
"""
info_df = pd.DataFrame(all_info, columns = ['Feature', 'Method', 'Cost Function', 'Number of Changepoints', 'Minimum Gap Between Changepoints', 'Penalty', 'Window Size', 'Position'])

"""
Save table
"""
info_df.to_csv(cpt_table_name, index=False)
