# Imports
from regression_helper import un_normalize
from time_series_smoothing import smoothing
from matplotlib.gridspec import GridSpec
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

pd.set_option('display.max_rows', 500)

"""
var_forecasts.py produces Figure S2 in the supplementary materials, which visualizes the 2023 forecasts produced by the Era 3 VAR
along with the Era 3 time series to contextualize them. Here, we also compare the forecast values with the
actual 2023 feature values.

You need to specify the root directory.

Inputs:
        - .csv of the smoothed time series
        - .csv of the unsmoothed time series
        - .csv of the feature values, not averaged by year (for the 2023 values)
        - .csv of VAR forecasts
Outputs:
        - .png containing Figure 3
        - .csv of percent errors between the VAR forecasts for 2023 and the actual 2023 feature values
"""

"""
DIRECTORIES
"""

# SPECIFY ROOT DIRECTORY
base_dir = "/Users/madelinehamilton/Documents/python_stuff/tar_repo/"

# Directory for smoothed time series
ts_filename = os.path.join(base_dir, "output_data/time_series/smoothed_time_series.csv")

# Directory for unsmoothed time series
ts_unsmoothed_filename = os.path.join(base_dir, "output_data/time_series/unsmoothed_time_series.csv")

# Directory for the VAR forecasts
var_forecast_filename = os.path.join(base_dir, "output_data/reg_results/VAR/era_3_var_forecasts.csv")

# Directory of feature dataset
feature_df_dir = os.path.join(base_dir, "output_data/features/all_features.csv")

# Directory for Figure 3
figure_3_filename = os.path.join(base_dir, "output_data/visualizations/var_forecasts.png")

# Directory for prediction errors
error_table_filename = os.path.join(base_dir, "output_data/reg_results/tables_for_paper/forecast_errors.csv")

"""
DATA PREPARATION
"""

# Read in the smoothed and unsmoothed time series
ts_df = pd.read_csv(ts_filename).dropna().reset_index(drop=True)
ts_unsmoothed_df = pd.read_csv(ts_unsmoothed_filename)
# Read in the VAR forecasts
forecast_df = pd.read_csv(var_forecast_filename)
# Read in the feature dataset, get only the 2023 feature values, average by year
feature_df = pd.read_csv(feature_df_dir)
actual_vals_df = feature_df.loc[feature_df['Year'].isin([2023])]
actual_vals_df = actual_vals_df.groupby('Year').mean()
actual_vals_df = actual_vals_df.reset_index(level=0)


"""
Currently, the forecasted values are normalized. We need to 'de-normalize' them so we can visualize them with the original
time series.
"""

features = list(ts_df.columns[1:])
un_normalized_forecasts = {'Year': 2023}

for feat in features:
    orig = list(ts_df[feat])
    new = list(forecast_df[feat])
    un_normalized_forecasts[feat] = un_normalize(orig, new)

forecast_df = pd.DataFrame.from_dict(un_normalized_forecasts)

"""
Figure 3 visualizes all eight features for 2000 - 2023. 2000 - 2020 values will come from the smoothed time series.
2021 - 2022 values will be 2-backward smoothed (1/3((year - 2) + (year - 1) + year))). 2023 values will come from the
actual 2023 DataFrame and will also be backward-smoothed. The 2023 forecast values do not need to be smoothed,
because the VAR uses smoothed time series already (therefore the forecast is the smoothed value prediction)

Concatenate the time series accordingly.
"""

# We need three DataFrames: historic DataFrame, historic + actual 2023 and historic + var_forecasts
ts_unsmoothed_actual = ts_unsmoothed_df.append(actual_vals_df).reset_index(level=0).drop(columns=['index'])

# List of lists to pass to the smoothing function
last_years = ts_unsmoothed_actual.tail(5)[features].values.tolist()
last_years = list(map(list, zip(*last_years)))

# Smooth
smoothed_lists = smoothing(last_years, forward=0, backward=2)
smoothed_lists = [lst[2:] for lst in smoothed_lists]
smoothed_lists = list(map(list, zip(*smoothed_lists)))

# Turn into DataFrame
last_years_df = pd.DataFrame(smoothed_lists, columns = features)
# Create a version without 2023 so we can add the forecast
last_years_minus_df = last_years_df.drop(last_years_df.tail(1).index)

# Historic DF
historic_df = ts_df.append(last_years_minus_df)
historic_df = historic_df.reset_index(drop=True)
historic_df = historic_df[48:]

# Historic + actual 2023
all_df = ts_df.append(last_years_df)
all_df = all_df.reset_index(drop=True)
all_df = all_df[48:]

# Historic + forecasted 2023
hist_plus_forecasted = ts_df.append(last_years_minus_df)
hist_plus_forecasted = hist_plus_forecasted.append(forecast_df)
hist_plus_forecasted = hist_plus_forecasted.reset_index(drop=True)
hist_plus_forecasted = hist_plus_forecasted[48:]

"""
Create and save Figure 3.
"""

# Matplotlib settings
plt.style.use('default')
plt.rcParams['figure.dpi'] = 800
plt.rcParams['savefig.dpi'] = 800
plt.rcParams['font.family'] = "Arial"
plt.rcParams['font.size'] = 8
plt.rcParams['legend.fontsize'] = 9
sns.set_context('paper', font_scale=0.9)
plt.rcParams['figure.constrained_layout.use'] = True

# X axis values and ticks
years = list(range(2000, 2023))
years_forecast = list(range(2000, 2024))

years_for_ticks = list(range(2000, 2023))
years_ticks = years_for_ticks[0::10]

# Initialize figure
fig = plt.figure(constrained_layout=True, figsize=(6.5, 4.0))
gs = GridSpec(2, 4, figure=fig)

# Tonal Strength
title_string =  'Tonal_S'
ax0 = fig.add_subplot(gs[0, :1])
ax0.plot(years, list(historic_df[title_string]), label = 'Historic Values', zorder = 10)
ax0.plot(years_forecast, list(hist_plus_forecasted[title_string]), label = 'Forecast 2023 Value', zorder = 0)
ax0.plot(years_forecast, list(all_df[title_string]), label = 'Actual 2023 Value', zorder = 0)
ax0.set_xticks(years_ticks)
ax0.set_yticks([0.68, 0.70, 0.72, 0.74])
ax0.set_ylabel('correlation coef.')
ax0.title.set_text('Tonal S.')

# MIC
title_string =  'PIC'
ax1 = fig.add_subplot(gs[0, 1:2])
ax1.plot(years, list(historic_df[title_string]), label = 'Historic Values', zorder = 10)
ax1.plot(years_forecast, list(hist_plus_forecasted[title_string]), label = 'Forecast 2023 Value', zorder = 0)
ax1.plot(years_forecast, list(all_df[title_string]), label = 'Actual 2023 Value', zorder = 0)
ax1.set_xticks(years_ticks)
ax1.set_yticks([2.75, 3.0, 3.25])
ax1.set_ylabel('bits')
ax1.title.set_text('PIC')

# Pitch STD
title_string = 'Pitch_SD'
ax2 = fig.add_subplot(gs[0, 2:3])
ax2.plot(years, list(historic_df[title_string]), label = 'Historic Values', zorder = 10)
ax2.plot(years_forecast, list(hist_plus_forecasted[title_string]), label = 'Forecast 2023 Value', zorder = 0)
ax2.plot(years_forecast, list(all_df[title_string]), label = 'Actual 2023 Value', zorder = 0)
ax2.set_xticks(years_ticks)
ax2.set_yticks([2.45,2.6,2.75,2.9])
ax2.set_ylabel('MIDI note #s')
ax2.title.set_text('Pitch SD')

# MIS
title_string = 'MIS'
ax3 = fig.add_subplot(gs[0, 3:4])
ax3.plot(years, list(historic_df[title_string]), label = 'Historic Values', zorder = 10)
ax3.plot(years_forecast, list(hist_plus_forecasted[title_string]), label = 'Forecast 2023 Value', zorder = 0)
ax3.plot(years_forecast, list(all_df[title_string]), label = 'Actual 2023 Value', zorder = 0)
ax3.set_xticks(years_ticks)
ax3.set_ylabel('MIDI note #s')
ax3.title.set_text(title_string)

# Onset Density
title_string = 'Onset_Density'
ax4 = fig.add_subplot(gs[1, :1])
ax4.plot(years, list(historic_df[title_string]), label = 'Historic Values', zorder = 10)
ax4.plot(years_forecast, list(hist_plus_forecasted[title_string]), label = 'Forecast 2023 Value', zorder = 0)
ax4.plot(years_forecast, list(all_df[title_string]), label = 'Actual 2023 Value', zorder = 0)
ax4.set_xticks(years_ticks)
ax4.set_yticks([2.4, 2.7, 3.0])
ax4.set_xlabel('Year')
ax4.set_ylabel('notes/second')
ax4.title.set_text('Onset Density')

# TI-OD
title_string = 'TI_OD'
ax5 = fig.add_subplot(gs[1, 1:2])
ax5.plot(years, list(historic_df[title_string]), label = 'Historic Values', zorder = 10)
ax5.plot(years_forecast, list(hist_plus_forecasted[title_string]), label = 'Forecast 2023 Value', zorder = 0)
ax5.plot(years_forecast, list(all_df[title_string]), label = 'Actual 2023 Value', zorder = 0)
ax5.set_xticks(years_ticks)
ax5.set_xlabel('Year')
ax5.set_yticks([5.0, 5.75, 6.5, 7.25])
ax5.set_ylabel('notes/bar')
ax5.title.set_text('TI-OD')

# ISO
title_string = 'ISO'
ax6 = fig.add_subplot(gs[1, 2:3])
ax6.plot(years, list(historic_df[title_string]), label = 'Historic Values', zorder = 10)
ax6.plot(years_forecast, list(hist_plus_forecasted[title_string]), label = 'Forecast 2023 Value', zorder = 0)
ax6.plot(years_forecast, list(all_df[title_string]), label = 'Actual 2023 Value', zorder = 0)
ax6.set_xticks(years_ticks)
ax6.set_xlabel('Year')
ax6.set_yticks([0.45, 0.5, 0.55, 0.6])
ax6.set_ylabel('proportion')
ax6.title.set_text(title_string)

# RIC
title_string = 'RIC'
ax7 = fig.add_subplot(gs[1, 3:4])
ax7.plot(years, list(historic_df[title_string]), label = 'Historic Values', zorder = 10)
ax7.plot(years_forecast, list(hist_plus_forecasted[title_string]), label = 'Forecast 2023 Value', zorder = 0)
ax7.plot(years_forecast, list(all_df[title_string]), label = 'Actual 2023 Value', zorder = 0)
ax7.set_xticks(years_ticks)
ax7.set_xlabel('Year')
ax7.set_ylabel('bits')
ax7.legend(loc='center right', bbox_to_anchor=(2.5, 1.4))
ax7.title.set_text(title_string)

# Save figure
plt.savefig(figure_3_filename, bbox_inches='tight')

"""
COMPARE WITH ACTUAL 2023 VALUES
"""

# Compute errors between the predicted and actual values
feats = list(actual_vals_df.columns[1:])
errors = []
nrmses = []

# Iterate through the feature list
for feat in feats:
    actual_val = list(actual_vals_df[feat])[0]
    forecast_val = list(forecast_df[feat])[0]
    # Percent difference
    error = 100*(forecast_val - actual_val) / actual_val
    errors.append(round(error,4))
    # Normalized root mean squared error
    # We normalize by the standard deviation of the relevant time series, from 2000 onwards
    smoothed_feat = list(ts_df[feat][48:])
    feat_sd = np.std(smoothed_feat)
    nrmse = np.sqrt((forecast_val - actual_val)**2) / feat_sd
    nrmses.append(round(nrmse, 4))

# Average percent error
mean_error = sum(errors) / len(errors)
print("Average percent error between actual and predicted 2023 features values:", round(mean_error, 2))

# Average nRMSE
mean_nrmse = sum(nrmses) / len(nrmses)
print("Average nRMSE between actual and predicted 2023 features values:", round(mean_nrmse, 2))

df_cols = ['Feature', 'Percent Error', 'nRMSE']
df = pd.DataFrame(list(zip(feats, errors, nrmses)), columns = df_cols)
df.to_csv(error_table_filename, index=False)
