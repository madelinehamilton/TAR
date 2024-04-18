# Imports
from statsmodels.tsa.ar_model import AutoReg
from sklearn.linear_model import LinearRegression
from regression_helper import normalize, nrmse_range
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import math
import statsmodels.api as sm

"""
autoregression_residuals.py fits autoregressive models for each feature, for each era, and saves the residuals for
future regressions. Each era has a maximum lag derived from the number of observations to encourage parsimony. Within
each era, the best (yielding the best nRMSE) lag for each feature is found. An autoregressive model for each feature is
fitted, and the residuals are saved.

You need to specify the root directory. If you get changepoint results that indicate different eras, you will need to
segment the time series manually.

Input: .csv with the (normalized) smoothed time series
Outputs:
        - .csv storing the lags and nRMSE values for each AR model (for Table 2 of the paper)
        - .csv storing the residuals from all the autoregression fits, for regression later
"""


"""
DIRECTORIES
"""

# SPECIFY ROOT DIRECTORY
base_dir = "/Users/madelinehamilton/Documents/python_stuff/tar_repo/"

# Directory of smoothed time series
ts_filename = os.path.join(base_dir, "output_data/time_series/norm_time_series.csv")

# Directories for output residuals (one per era)
resid_dir_1 = os.path.join(base_dir, "output_data/reg_results/residuals/era_1_residuals.csv")
resid_dir_2 = os.path.join(base_dir, "output_data/reg_results/residuals/era_2_residuals.csv")
resid_dir_3 = os.path.join(base_dir, "output_data/reg_results/residuals/era_3_residuals.csv")

# Table 2 directory
table_2_dir = os.path.join(base_dir, "output_data/reg_results/tables_for_paper/table_2.csv")

"""
DATA PREPARATION
"""

# Read in the data
ts_df = pd.read_csv(ts_filename)
# Drop the 'Year column'
ts_df = ts_df.drop('Year', axis=1)

"""
With changepoint detection, we found three eras: 1950 - 1974, 1975 - 1999, and 2000 - 2022. We need to divide
the time series into these eras and perform autoregression per era.
"""
seg1 = ts_df.iloc[0:25].dropna().reset_index(drop=True)
seg2 = ts_df.iloc[25:50].dropna().reset_index(drop=True)
seg3 = ts_df.iloc[50:].dropna().reset_index(drop=True)
eras = [seg1, seg2, seg3]

"""
ANALYSIS
"""

"""
Fit an autoregressive model for each feature. We need to determine the optimal lag per feature per era,
with a maximum lag dependent on the length of the era in years.

Then, fit the autoregressive model with optimal lag, compute the nRMSE and residuals and store these in
new DataFrames.

We also need to be storing the best lags and nRMSEs for each feature and era for Table 2 of the paper.
"""

seg1_maxlag = 5
seg2_maxlag = 5
seg3_maxlag = 4

maximum_lags = [seg1_maxlag, seg2_maxlag, seg3_maxlag]

new_eras = []
results_dfs = []

# Initial storing of results for Table 2
# Idk if this is optimal but computer science is hard
empty_tallies = [[]]*len(ts_df.columns)
ar_results = dict(zip(list(ts_df.columns), empty_tallies))

# Iterate through the era time series
for i in range(len(eras)):
    df = eras[i]
    max_lag = maximum_lags[i]
    # Empty DataFrame for the residuals
    new_df = pd.DataFrame(columns=df.columns)
    # Empty DataFrame for autoregression results
    results_string_1 = 'Era ' + str(i+1) + ' nRMSE'
    results_string_2 = 'Era ' + str(i+1) + ' Lag'
    results_df_columns = [results_string_1, results_string_2]
    results_df = pd.DataFrame(columns=results_df_columns)
    results_df['Feature'] = list(df.columns)
    results_df = results_df.set_index('Feature')

    # Empty lists to store best nRMSEs and lags
    best_nrmses = []
    best_lags = []

    # Iterate through all the features
    for col in ts_df.columns:
        # Get the feature
        series = df[col]
        # List to store nRMSEs of the different lags
        nrmses = []
        # Iterate through all possible lags
        for l in range(1, max_lag + 1):
            # Fit model with lag
            model = AutoReg(series, lags = l, old_names = True)
            # Get the fitted values
            results = model.fit()
            fitted = list(results.fittedvalues)
            # Add the first l elements of the original time series to the beginning of the fitted values
            # This is for nRMSE purposes: an AR model of lag l cannot produce fitted values for the first
            # l elements, so the first l elements will just be the original values
            first_l = list(series)[:(l+1)]
            fitted = first_l + fitted
            # Compute nRMSE between fitted and original values
            nrmse = nrmse_range(list(series), fitted)
            nrmses.append(round(nrmse, 2))

        # Choose the lag with the lowest nRMSE
        best_nrmse = min(nrmses)
        best_lag = nrmses.index(min(nrmses)) + 1

        # Fit a model with this lag
        model = AutoReg(series, lags = best_lag, old_names = True)
        results = model.fit()
        # Get the residuals
        residuals = list(results.resid)
        # Put N/A for the first best_lag values (as explained in the above comment)
        residuals = [np.nan]*best_lag + residuals
        # The "new" version of the feature is now the residuals. Store this
        new_df[col] = residuals

        # Store best nRMSE and lag
        best_nrmses.append(best_nrmse)
        best_lags.append(best_lag)

    # Store best results for the era
    results_df[results_string_1] = best_nrmses
    results_df[results_string_2] = best_lags
    results_dfs.append(results_df)

    # Store the residuals for each era
    new_eras.append(new_df)

# Combine the three results DataFrames
table_2_df = pd.concat(results_dfs, axis=1)

"""
Finally, write out the residuals for future regression, and the AR model info for Table 2.
"""

new_eras[0].to_csv(resid_dir_1, index=False)
new_eras[1].to_csv(resid_dir_2, index=False)
new_eras[2].to_csv(resid_dir_3, index=False)

table_2_df.to_csv(table_2_dir)
