# Imports
from regression_helper import normalize, nrmse_range
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.api import VAR
import os
import pandas as pd
import numpy as np
import scipy.stats

"""
vector_autoregression.py performs vector autoregression on the DOM smoothed time series. The time series are divided
into segments per the results of changepoint analysis, and VAR models are fit separately per segment.

Inputs: .csv containing the (normalized) smoothed time series
Outputs:
        - .csv's with model coefficients for each era
        - .csv with 2023 forecasts generated by the Era 3 VAR

You need to specify the root directory. If you get changepoint results that indicate different eras, you will need to
segment the time series manually.

Note: there is a manual aspect to this script. Here's how I recommend going through it:

      1. Comment out everything below the saving of the model coeffients (below the comment 'Finally, save the forecasts and model coefficients.')

      2. Run the script with that portion of the script commented out. A bunch of equations will be printed, which give the
         VAR coefficients for each of the three models.

      3. Uncomment the previously commented out portion of the code. Use the printed coefficients to manually edit the
         lists at the bottom (era_1_ys, era_1_predictors, era_1_lags, era_1_coefficients, etc.).
         I take out the statistically insignificant coefficients.

      4. Run the script again to save the coefficients.

I apologize about the manual insertion of the coefficients. I couldn't figure out how to extract significant
coefficients automatically from the statsmodel object that is returned when you fit the model; I only know how to print the coefficients out.
"""

# SPECIFY ROOT DIRECTORY
base_dir = "/Users/madelinehamilton/Documents/python_stuff/tar_repo/"

# Directory of the smoothed time series
ts_filename = os.path.join(base_dir, "output_data/time_series/norm_time_series.csv")

# Directories to save models (for Figure 2 in another script)
era_1_model_filename = os.path.join(base_dir, "output_data/reg_results/VAR/era_1_var_coefficients.csv")
era_2_model_filename = os.path.join(base_dir, "output_data/reg_results/VAR/era_2_var_coefficients.csv")
era_3_model_filename = os.path.join(base_dir, "output_data/reg_results/VAR/era_3_var_coefficients.csv")

# Directory to save the Era 3 VAR forecasts (for Figure S2 in another script)
forecasts_filename = os.path.join(base_dir, "output_data/reg_results/VAR/era_3_var_forecasts.csv")

# Pandas display settings
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 200)

"""
DATA PREPARATION
"""

# Read in the time series
ts_df = pd.read_csv(ts_filename)
# Drop the 'Year column'
ts_df = ts_df.drop('Year', axis=1)

# Era 1: 1950 - 1974
# Era 2: 1975 - 1999
# Era 3: 2000 - 2022

# Segment the data into its eras
era_1 = ts_df.iloc[0:25].dropna().reset_index(drop=True)
era_2 = ts_df.iloc[25:50].dropna().reset_index(drop=True)
era_3 = ts_df.iloc[50:].dropna().reset_index(drop=True)

eras = [era_1, era_2, era_3]

"""
ANALYSIS
"""

"""
First, we need to perform Granger's causality tests per era, so we can determine which features are suitable
for VAR.

grangers_causation_matrix() computes the Granger causality of all possible combinations of the time series. The rows
are the response variable, columns are predictors. The values in the table are the p-values. p-values lesser than the
significance level (0.05) implies the null hypothesis that the coefficients of the corresponding past values is zero,
that is, the hypothesis that X does not cause Y can be rejected.
"""

def grangers_causation_matrix(data, variables, test='ssr_chi2test'):

    maxlag=3
    test = 'ssr_chi2test'
    # Initialize matrix
    df = pd.DataFrame(np.zeros((len(variables), len(variables))), columns=variables, index=variables)
    # Iterate through all combinations of time series
    for c in df.columns:
        for r in df.index:
            # Grangers causality test from statsmodels
            test_result = grangercausalitytests(data[[r, c]], maxlag=maxlag, verbose=False)
            # Get best p value
            p_values = [round(test_result[i+1][0][test][1],4) for i in range(maxlag)]
            min_p_value = np.min(p_values)
            # Store p value
            df.loc[r, c] = min_p_value
    # Label rows and columns of matrix
    df.columns = [var + '_x' for var in variables]
    df.index = [var + '_y' for var in variables]
    return df

# Instantiate list of features suitable for VAR for each era
suit_feat_list = []

# Granger's causality matrix for each era
for i in range(len(eras)):
    era = eras[i]
    grangers_mat = grangers_causation_matrix(era, variables = era.columns)

    # Now we need to decide if each feature is suitable for vector autoregression
    feat_list = list(era.columns)
    suitable_features = []
    for feat in feat_list:
        x_name = feat + '_x'
        y_name = feat + '_y'
        # Get the row and column that corresponds to the feature
        row = grangers_mat.loc[y_name]
        column = grangers_mat[x_name]

        # We don't care about the diagonals, so we need to remove them
        row = list(row.drop(labels=[x_name]))
        column = list(column.drop(labels=[y_name]))

        # Count the number of times we have a p value below 0.05
        row_count = len([x for x in row if x < 0.05])
        column_count = len([x for x in column if x < 0.05])
        total_count = row_count + column_count

        # If the total count is 2 or more, then we say the feature is suitable for VAR
        if total_count > 1:
            suitable_features.append(feat)


    # Store suitable feature list
    suit_feat_list.append(suitable_features)


"""
Here, features not suitable for VAR are dropped. In this case, all features in all eras meet the criteria.
"""

era_1_columns = suit_feat_list[0]
era_2_columns = suit_feat_list[1]
era_3_columns = suit_feat_list[2]

era_1 = era_1[era_1_columns]
era_2 = era_2[era_2_columns]
era_3 = era_3[era_3_columns]

eras = [era_1, era_2, era_3]

"""
Next we need to find the optimal lag for each VAR. We don't care so much about parsimony here, so I don't impose
a maximum lag.
"""

models = []
lags = []
# For each era, create a model and call select_order()
for i in range(len(eras)):
    era = eras[i]
    model = VAR(era)
    models.append(model)
    results = model.select_order()
    best_lag = results.selected_orders['bic']
    lags.append(best_lag)

"""
Fit the models with the optimal lags.
"""

models_fitted = []
for i in range(len(models)):
    model_fitted = models[i].fit(lags[i])
    models_fitted.append(model_fitted)
    print(model_fitted.summary())

"""
For the Era 3 model, produce the 2023 forecasts.
"""

era_3_model = models_fitted[2]
era_3_lag = lags[2]
initial_values = era_3.values[1:]
forecast_vals = [era_3_model.forecast(initial_values, 3)[2]]
forecast_df = pd.DataFrame(forecast_vals, columns = eras[1].columns)

"""
Finally, save the forecasts and model coefficients.
"""

era_1_ys = ['Pitch_SD', 'Pitch_SD', 'MIS', 'MIS', 'MIS', 'MIS', 'MIS', 'Onset_Density', 'TI_OD', 'TI_OD', 'ISO', 'PIC','PIC','PIC','PIC','PIC','RIC', 'RIC']
era_1_predictors = ['Pitch_SD', 'ISO', 'const', 'Tonal_S', 'MIS', 'ISO', 'RIC', 'Tonal_S', 'TI_OD', 'RIC', 'ISO', 'const', 'Pitch_SD', 'TI_OD', 'ISO', 'RIC', 'MIS', 'RIC']
era_1_lags = [1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1]
era_1_coefs = [0.8539, -0.7826, 1.090, -0.5670, 0.4396, -0.8982, -0.4619, 0.1514, 0.6848, 0.2624, 0.6710, 1.113, 0.3946, -0.7923, -0.5435, -0.4549, 0.6774, 0.7408]

era_2_ys = ['Tonal_S', 'Tonal_S', 'Pitch_SD', 'MIS', 'MIS', 'Onset_Density', 'Onset_Density', 'Onset_Density', 'TI_OD', 'TI_OD', 'TI_OD', 'ISO', 'ISO', 'RIC', 'RIC', 'RIC']
era_2_predictors = ['Tonal_S', 'PIC', 'Pitch_SD', 'Tonal_S', 'ISO', 'Tonal_S', 'MIS', 'ISO', 'TI_OD', 'ISO', 'PIC', 'TI_OD', 'ISO', 'MIS', 'TI_OD', 'PIC']
era_2_lags = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
era_2_coefs = [0.5096, -1.587, 0.6115, -0.3369, 0.6748, 0.1421, -0.2947, -0.4856, 1.202, -0.3435, 0.4266, 0.5204, 0.5856, 0.5257, -1.035, -1.088]

era_3_ys = ['Tonal_S', 'Tonal_S', 'Pitch_SD','Pitch_SD','Pitch_SD', 'MIS', 'MIS', 'TI_OD', 'ISO','ISO','ISO','ISO','ISO','ISO', 'PIC', 'PIC', 'RIC', 'RIC', 'RIC', 'RIC', 'RIC', 'RIC']
era_3_predictors = ['MIS', 'PIC', 'MIS', 'TI_OD', 'RIC', 'Onset_Density', 'TI_OD', 'TI_OD', 'const', 'Tonal_S', 'Pitch_SD', 'Onset_Density', 'ISO', 'RIC', 'MIS', 'PIC', 'const', 'Tonal_S', 'Pitch_SD', 'Onset_Density', 'ISO', 'RIC']
era_3_lags = [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1]
era_3_coefs = [-2.000, 2.426, -1.049, 0.3737, 1.670, -0.9762, 0.9454, 1.041, -2.376, -0.8600, -2.046, 1.274, 2.254, 3.054, -0.4502, 0.9063, 2.276, -0.5322, 1.149, -0.9176, -1.461, -2.026]

era_1_df = pd.DataFrame(list(zip(era_1_ys, era_1_predictors, era_1_lags, era_1_coefs)), columns =['Dependent', 'Predictor', 'Lag', 'Coefficient'])
era_2_df = pd.DataFrame(list(zip(era_2_ys, era_2_predictors, era_2_lags, era_2_coefs)), columns =['Dependent', 'Predictor', 'Lag', 'Coefficient'])
era_3_df = pd.DataFrame(list(zip(era_3_ys, era_3_predictors, era_3_lags, era_3_coefs)), columns =['Dependent', 'Predictor', 'Lag', 'Coefficient'])

era_1_df.to_csv(era_1_model_filename, index = False)
era_2_df.to_csv(era_2_model_filename, index = False)
era_3_df.to_csv(era_3_model_filename, index = False)

forecast_df.to_csv(forecasts_filename, index = False)
