# Imports
import pandas as pd
import os

"""
per_era_averages.py computes feature averages per era. Changepoint detection should have identified
a few changepoints for the time series. Segmenting the time series with these changepoints will create distinct eras.
Eras are hard-coded, so if you have different changepoints, you need to edit this script to reflect that.

You need to specify the root directory.
"""

"""
DIRECTORIES
"""
# SPECIFY ROOT DIRECTORY
base_dir = "/Users/madelinehamilton/Documents/python_stuff/tar_repo/"

# All features .csv directory
features_dir = os.path.join(base_dir, "output_data/features/all_features.csv")

"""
DATA PREPARATION
"""
# Read in the .csv
df = pd.read_csv(features_dir)

# Divide into eras: Era 1 is 1950 - 1974, Era 2 is 1975 - 1999, and Era 3 is 2000 - 2022.
era_1_years = list(range(1950, 1975))
era_2_years = list(range(1975, 2000))
era_3_years = list(range(2000, 2023))

era_1_df = df.loc[df['Year'].isin(era_1_years)]
era_2_df = df.loc[df['Year'].isin(era_2_years)]
era_3_df = df.loc[df['Year'].isin(era_3_years)]

"""
ANALYSIS
"""
# For each era, print the MIS, Pitch SD, Onset Density, and TI-OD average
eras = [era_1_df, era_2_df, era_3_df]

for i in range(len(eras)):
    era = eras[i]
    mis_mean = era.loc[:, 'MIS'].mean()
    pitch_sd_mean = era.loc[:, 'Pitch_SD'].mean()
    od_mean = era.loc[:, 'Onset_Density'].mean()
    ti_od_mean = era.loc[:, 'TI_OD'].mean()

    print("Era", i+1, "averages:")
    print("MIS:", round(mis_mean, 2))
    print("Pitch SD:", round(pitch_sd_mean, 2))
    print("Onset Density:", round(od_mean, 2))
    print("TI-OD:", round(ti_od_mean, 2))
    print()
