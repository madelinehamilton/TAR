# Imports
from regression_helper import normalize, nrmse_range, compute_model_values
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns

"""
var_fits.py produces Figure 2 in the paper, which visualizes the 3 best fits produced by the VARs. The
VAR fitted values and their nRMSEs are computed, the 3 best fits are selected, and then these are visualized.

Note: there is some manual editing here. A table of the VAR equations with their nRMSE values is printed, and then
I picked the fits I wanted to visualize based on the nRMSE values I saw. Because of this, I'd recommend commenting out everything below the printing
of the table when first running the code, and then editing that code to reflect the fits you want to visualize.

You need to specify the root directory. If you get changepoint results that indicate different eras, you will need to
segment the time series manually.

Inputs:
        - .csv with the (normalized) smoothed time series (the original values, against which the VAR fitted values will be compared)
        - .csv's with the VAR coefficients for each of the eras so the fitted values can be computed
Outputs:
        - .png with Figure 2
"""

# SPECIFY BASE DIRECTORY
base_dir = "/Users/madelinehamilton/Documents/python_stuff/tar_repo/"

# Directory for smoothed time series
ts_filename = os.path.join(base_dir, "output_data/time_series/norm_time_series.csv")

# Directory for the model coefficients
era_1_model_filename = os.path.join(base_dir, "output_data/reg_results/VAR/era_1_var_coefficients.csv")
era_2_model_filename = os.path.join(base_dir, "output_data/reg_results/VAR/era_2_var_coefficients.csv")
era_3_model_filename = os.path.join(base_dir, "output_data/reg_results/VAR/era_3_var_coefficients.csv")

# Directory for Fig 2.
figure_2_filename = os.path.join(base_dir, "output_data/visualizations/var_best_fits.png")

"""
DATA PREPARATION
"""
# Read in the time series
ts_df = pd.read_csv(ts_filename)
# Drop the 'Year column'
ts_df = ts_df.drop('Year', axis=1)

# Segment the data into its eras
era_1 = ts_df.iloc[0:25].dropna().reset_index(drop=True)
era_2 = ts_df.iloc[25:50].dropna().reset_index(drop=True)
era_3 = ts_df.iloc[50:].dropna().reset_index(drop=True)

# Model coefficients
var_1_info = pd.read_csv(era_1_model_filename)
var_2_info = pd.read_csv(era_2_model_filename)
var_3_info = pd.read_csv(era_3_model_filename)

"""
ANALYSIS
"""

"""
Determine the best fits to display for Figure 2 by creating tables which list the nRMSEs between the original and
VAR fitted values for each feature.
"""

era_1_model = compute_model_values(era_1, var_1_info)
era_2_model = compute_model_values(era_2, var_2_info)
era_3_model = compute_model_values(era_3, var_3_info)

nrmses_1 = []
for item in era_1_model.items():
    era = 1
    feature_name = item[0]
    error = item[1][2]
    nrmses_1.append([era, feature_name, error])

nrmses_1_df = pd.DataFrame(nrmses_1, columns = ['Era', 'Feature', 'nRMSE'])

nrmses_2 = []
for item in era_2_model.items():
    era = 2
    feature_name = item[0]
    error = item[1][2]
    nrmses_2.append([era, feature_name, error])

nrmses_2_df = pd.DataFrame(nrmses_2, columns = ['Era', 'Feature', 'nRMSE'])

nrmses_3 = []
for item in era_3_model.items():
    era = 3
    feature_name = item[0]
    error = item[1][2]
    nrmses_3.append([era, feature_name, error])

nrmses_3_df = pd.DataFrame(nrmses_3, columns = ['Era', 'Feature', 'nRMSE'])
nrmses_2_df = nrmses_2_df.append(nrmses_3_df)
nrmses_1_df = nrmses_1_df.append(nrmses_2_df)
nrmses_1_df = nrmses_1_df.sort_values('nRMSE')
print(nrmses_1_df)

"""
It looks like Era 1 PIC, Era 2 TI-OD, and Era 3 ISO give the best fits (nRMSE = 0.11, 0.17, 0.19, respectively)

We need to visualize these to produce Figure 2 in the paper.
"""

"""
Get the original and fitted values for the three features
"""

# PIC Era 1
pic_era_1_original = era_1_model['PIC'][0]
pic_era_1_fitted = era_1_model['PIC'][1]

# ISO Era 2
iso_era_2_original = era_2_model['ISO'][0]
iso_era_2_fitted = era_2_model['ISO'][1]

# TI-OD Era 3
ti_od_era_3_original = era_3_model['TI_OD'][0]
ti_od_era_3_fitted = era_3_model['TI_OD'][1]

"""
Figure preparation
"""

# Get the 3 nRMSE values and make strings for the figures
pic_nrmse = round(era_1_model['PIC'][2], 2)
ti_od_nrmse = round(era_3_model['TI_OD'][2], 2)
iso_nrmse = round(era_2_model['ISO'][2], 2)

pic_nrmse_string = 'nRMSE = ' + str(pic_nrmse)
ti_od_nrmse_string = 'nRMSE = ' + str(ti_od_nrmse)
iso_nrmse_string = 'nRMSE = ' + str(iso_nrmse)

# Matplotlib settings
plt.style.use('default')
plt.rcParams['figure.dpi'] = 800
plt.rcParams['savefig.dpi'] = 800
plt.rcParams['font.family'] = "Arial"
plt.rcParams['font.size'] = 8
plt.rcParams['legend.fontsize'] = 9
sns.set_context('paper', font_scale=0.9)
plt.rcParams['figure.constrained_layout.use'] = True

# Initialize figure
fig = plt.figure(constrained_layout=True, figsize=(6.5, 3.0))
gs = GridSpec(2, 3, figure=fig)

# X axis values and ticks for the plots
# Era 1
years_seg1 = list(range(1952, 1975))
years_seg1_string = '1952-1974'
years_seg1_ticks = [1955, 1965, 1975]
# Era 2
years_seg2 = list(range(1975, 2000))
years_seg2_string = '1975-1999'
years_seg2_ticks = [1975, 1985, 1995]
# Era 3
years_seg3 = list(range(2000, 2021))
years_seg3_string = '2000-2020'
years_seg3_ticks = years_seg3[0::5]

# PIC Era 1
title_string =  'PIC' + " " + years_seg1_string
ax0 = fig.add_subplot(gs[0, :1])
ax0.plot(years_seg1, pic_era_1_original, label = 'Feature Values')
ax0.plot(years_seg1, pic_era_1_fitted, label = 'Model Values')
ax0.set_xticks(years_seg1_ticks)
ax0.set_yticks([0.55, 0.70, 0.85, 1.0])
ax0.set_ylabel('Normalized Feature Value')
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax0.text(0.3, 0.95, pic_nrmse_string, transform=ax0.transAxes, fontsize=9, bbox=props, verticalalignment='top')
ax0.title.set_text(title_string)

# ISO Era 2
title_string =  'ISO' + " " + years_seg2_string
ax1 = fig.add_subplot(gs[0, 1:2])
ax1.plot(years_seg2, iso_era_2_original, label = 'Feature Values')
ax1.plot(years_seg2, iso_era_2_fitted, label = 'Model Values')
ax1.set_xticks(years_seg2_ticks)
ax1.set_yticks([0.25, 0.35, 0.45, 0.55, 0.65])
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax1.text(0.10, 0.88, iso_nrmse_string, transform=ax1.transAxes, fontsize=9, bbox=props, verticalalignment='top')
ax1.title.set_text(title_string)

# TI-OD Era 3
title_string =  'TI-OD' + " " + years_seg3_string
ax2 = fig.add_subplot(gs[0, 2:3])
ax2.plot(years_seg3, ti_od_era_3_original, label = 'Feature Values')
ax2.plot(years_seg3, ti_od_era_3_fitted, label = 'Model Values')
ax2.set_xticks(years_seg3_ticks)
ax2.set_yticks([0.35, 0.6, 0.85, 1.10])
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax2.text(0.37, 0.93, ti_od_nrmse_string, transform=ax2.transAxes, fontsize=9, bbox=props, verticalalignment='top')
ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5))
ax2.title.set_text(title_string)

# Save plot
plt.savefig(figure_2_filename, bbox_inches='tight')
