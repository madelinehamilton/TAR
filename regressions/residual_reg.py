# Imports
from regression_helper import normalize, nrmse_range
from sklearn.linear_model import LinearRegression
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import math
import os
import pandas as pd
import statsmodels.api as sm
import scipy.stats

"""
residual_reg.py regresses the autoregression residuals of features computed previously against other features
(per era).

NOTE: Based on the univariate regression results, I explore some multilinear regressions. Therefore, I would comment
out the second portion of this code (from MULTILINEAR REGRESSION downwards) when you run it for the first time. Look
at table_3.csv, and based on what you see (within one era, are there dependents with multiple significant regressions?),
edit the second portion of the code to explore the multilinear regressions you want.

However, I would exercise caution with the multilinear regression: I figured out that, though the time series are
uncorrelated overall, they are pretty correlated within eras, leading to multicollinearity when I try to do multilinear
regression the vast majority of the time.

As with autoregression_residuals.py, segmentation of the time series into eras is hard-coded. If you want to segment them differently, you must manually
input the desired eras.

You need to specify the root directory. If you get changepoint results that indicate different eras, you will need to
segment the time series manually.

Inputs:
       - a .csv of (normalized) smoothed time series
       - .csv's of autoregression residuals for each era

Output: a .csv containing Table 3 in the paper: results of significant regressions (estimates, p-values, etc.)
"""

# SPECIFY ROOT DIRECTORY
base_dir = "/Users/madelinehamilton/Documents/python_stuff/tar_repo/"

# Directory of (normalized) smoothed time series
ts_filename = os.path.join(base_dir, "output_data/time_series/norm_time_series.csv")

# Directories of autoregression residuals
resid_1_filename = os.path.join(base_dir, "output_data/reg_results/residuals/era_1_residuals.csv")
resid_2_filename = os.path.join(base_dir, "output_data/reg_results/residuals/era_2_residuals.csv")
resid_3_filename = os.path.join(base_dir, "output_data/reg_results/residuals/era_3_residuals.csv")

# Directory for Table 3 .csv
table_3_filename = os.path.join(base_dir, "output_data/reg_results/tables_for_paper/table_3.csv")

"""
DATA PREPARATION
"""

# The original time series need to be normalized and segmented
original_ts_df = pd.read_csv(ts_filename)
# Drop the 'Year column'
original_ts_df = original_ts_df.drop('Year', axis=1)

seg1 = original_ts_df.iloc[0:25].dropna().reset_index(drop=True)
seg2 = original_ts_df.iloc[25:50].dropna().reset_index(drop=True)
seg3 = original_ts_df.iloc[50:].dropna().reset_index(drop=True)

original_eras = [seg1, seg2, seg3]

# Autoregression residuals for each era
era_1_residuals = pd.read_csv(resid_1_filename)
era_2_residuals = pd.read_csv(resid_2_filename)
era_3_residuals = pd.read_csv(resid_3_filename)

new_eras = [era_1_residuals, era_2_residuals, era_3_residuals]

"""
For each era, regress the residuals of one feature against the other 6 features. Keep regressions with R^2 values more
than 0.25 and p-values less than 0.05, and store the model info for Table 3.
"""

# This will store the regression results
reg_info = []
# Iterate through the eras
for i in range(len(new_eras)):
    # Get original time series and residuals for the era
    new_era_df = new_eras[i]
    old_df = original_eras[i]
    features = list(new_era_df.columns)

    # Iterate through each autoregression residual
    for dep in features:
        y_data = new_era_df[dep]

        # Remove NA values. Keep count of them so we know how to adjust the predictor data
        nan_count = sum([math.isnan(x) for x in list(y_data)])
        y_data = y_data.dropna()

        # Iterate through all possible predictors (all features except itself)
        for indep in features:
            if dep == indep:
                continue
            else:
                # Predictor
                x = old_df[indep][nan_count:]

                # Regression
                X2 = sm.add_constant(x)
                est = sm.OLS(list(y_data), X2)
                est2 = est.fit()
                # Get model info
                p_vals = est2.pvalues.to_dict()
                r_squared = est2.rsquared
                coefficient = est2.params[indep]

                # If p < 0.05
                if p_vals[indep] < 0.05:
                    # If R^2 >= 0.25
                    if r_squared >= 0.25:
                        # If the regression is significant, store its info
                        reg_info.append([i+1, dep, indep, round(coefficient, 3), round(p_vals[indep], 4), round(r_squared, 3)])

results_df = pd.DataFrame(reg_info, columns = ['Era', 'Dependent', 'Independent', 'Estimate', 'p-value', 'R^2'])

# Save the Table 3 DataFrame
results_df.to_csv(table_3_filename, index = False)

"""
MULTILINEAR REGRESSION
"""

"""
We want to try a multilinear regression of Onset Density in Era 3, with three possible variables:
ISO, PIC AND RIC.
"""

# Specify the regressions you'd like to explore
eras = [3]
dependents = ['Onset_Density']
independent_lists = [['ISO', 'PIC', 'RIC']]

for i in range(len(eras)):
    era = eras[i]
    original_data = original_eras[i]
    residual_data = new_eras[i]
    dep = dependents[i]
    indeps = independent_lists[i]

    # Get nan count, adjust
    residual = residual_data[dep]
    nan_count = sum([math.isnan(x) for x in list(residual)])
    residual = residual.dropna().reset_index(drop=True)

    # Get independents
    originals = []
    for indep in indeps:
        orig = list(original_eras[i][indep][nan_count:])
        originals.append(orig)

    originals = list(map(list, zip(*originals)))
    x_data = pd.DataFrame(originals, columns = indeps)

    # Regression
    X2 = sm.add_constant(x_data)
    est = sm.OLS(residual, X2)
    est2 = est.fit()

    # Get model info
    p_vals = est2.pvalues.to_dict()
    r_squared = est2.rsquared
    coefficients = est2.params.to_dict()

    # How are the results?
    print("Regressing", dep, "on", indeps, "in Era", era, ":")
    print("R squared:", r_squared)
    print("P value:", p_vals)

"""
We see that the multilinear regression is not great, so we'll just use the univariate regressions.
"""
