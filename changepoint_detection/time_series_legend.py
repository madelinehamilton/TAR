# Imports
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

"""
time_series_legend.py produces the legend for Figure 1, since I can't figure out how to do it properly in R.
A (messy, ugly) plot with all 8 time series is created. I screenshot the legend part of the figure only for Figure 1.

Input: .csv with the unsmoothed time series (could be smoothed, normalized, doesn't really matter)
Output: .png with the visualization
"""

"""
Set some Matplotlib / seaborn parameters
"""
plt.style.use('default')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 600
plt.rcParams['figure.figsize'] = (3.5,7)
#plt.rcParams['figure.autolayout'] = False
plt.rcParams['font.family'] = "Arial"
plt.rcParams['font.size'] = 8
plt.rcParams['legend.fontsize'] = 9
sns.set_context('paper', font_scale=1.0)

"""
DIRECTORIES
"""
# SPECIFY ROOT DIRECTORY
base_dir = "/Users/madelinehamilton/Documents/python_stuff/tar_repo/"

# Unsmoothed time series
unsmoothed_ts_name = os.path.join(base_dir, "output_data/time_series/unsmoothed_time_series.csv")
# Output directories for visualization
fig_dir = os.path.join(base_dir, "output_data/visualizations/timeseries_w_changepoints/legend.png")

"""
DATA PREPARATION
"""

# Read in the time series
unsmoothed_ts_df = pd.read_csv(unsmoothed_ts_name)

"""
VISUALIZATION
"""

# Create supfig
fig, axs = plt.subplots(8)

# Specify x axis range and ticks
all_years = list(range(1950, 2023))
x_ticks = [1950+(x*5) for x in list(range(0, 15))]

# Tonal Strength
axs[0].plot(all_years, unsmoothed_ts_df['Tonal_S'], color = '#F8766D', label = "Tonal S. (TS)")
axs[0].set_yticks([0.68, 0.72, 0.76])
axs[0].set_ylabel("corr. coef.")

# PIC
axs[1].plot(all_years, unsmoothed_ts_df['PIC'], color = '#C49A00', label = "PIC")
axs[1].set_yticks([3.0, 3.75, 4.5])
axs[1].set_ylabel("bits")

# Pitch SD
axs[2].plot(all_years, unsmoothed_ts_df['Pitch_SD'], color = '#53B400', label = "Pitch SD (PSD)")
axs[2].set_yticks([2.5, 3.0, 3.5])
axs[2].set_ylabel("MIDI note #s")

# MIS
axs[3].plot(all_years, unsmoothed_ts_df['MIS'], color = '#00C094', label = "MIS")
axs[3].set_yticks([1.8, 2.2, 2.6])
axs[3].set_ylabel("MIDI note #s")

# Onset Density
axs[4].plot(all_years, unsmoothed_ts_df['Onset_Density'], color = '#00B6EB', label = "Onset D. (OD)")
axs[4].set_yticks([1.8, 2.4, 3.0])
axs[4].set_ylabel("notes/s")

# TI-OD
axs[5].plot(all_years, unsmoothed_ts_df['TI_OD'], color = '#0052EB', label = "TI-OD")
axs[5].set_yticks([5, 10, 15])
axs[5].set_ylabel("notes/s")

# ISO
axs[6].plot(all_years, unsmoothed_ts_df['ISO'], color = '#A58AFF', label = "ISO")
axs[6].set_yticks([0.3, 0.45, 0.60])
axs[6].set_ylabel("proportion")

# RIC
axs[7].plot(all_years, unsmoothed_ts_df['RIC'], color = '#FB61D7', label = "RIC")
axs[7].set_yticks([1.75, 2.25, 2.75])
axs[7].set_xlabel("Year")
axs[7].set_ylabel("bits")

# Legend
fig.legend(bbox_to_anchor=(1.5, 0.52),loc = 'center right')
plt.tight_layout()

# Save figure
plt.savefig(fig_dir, bbox_inches='tight')
