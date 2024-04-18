# Imports
from time_series_smoothing import smoothing
import pandas as pd
import matplotlib.pyplot as plt
import math
import os

"""
produce_full_tar_dataset.py takes a .csv with a dataset of the 6 non-IDyOM features and merges it with two .dat files, each of
which contain one IDyOM feature. It also averages the features by year and smooths the resulting time series to produce the
data needed for the TAR changepoint detection and regressions.

You need to specify the root directory. Make sure the two IDyOM .dat files are named "pic_from_idyom.dat" and
"ric_from_idyom.dat" and have been placed in /output_data/features/.

Inputs:
       - .csv produced by compute_tar_features_no_idyom.py, which contains the TAR features not computed by IDyOM
       - Two .dat files, each with a TAR feature computed by IDyOM (the PIC and RIC features)
Outputs:
       - a .csv of a DataFrame containing all 8 TAR features computed per MIDI melody
       - a .csv of a DataFrame containing the 8 unsmoothed TAR time series
       - a .csv of a DataFrame containing the 8 smoothed TAR time series
       - a .csv of a DataFrame containing the 8 smoothed and normalized TAR time series
"""

"""
DIRECTORIES
"""

# SPECIFY BASE DIRECTORY
base_dir = "/Users/madelinehamilton/Documents/python_stuff/tar_repo/"

# PIC and RIC .dat files from IDyOM
pic_filename = os.path.join(base_dir, "output_data/features/pic_from_idyom.dat")
ric_filename = os.path.join(base_dir, "output_data/features/ric_from_idyom.dat")

# Non-IDyOM feature DataFrame
non_idyom_filename = os.path.join(base_dir, "output_data/features/non_idyom_features.csv")

# Output Directories
full_tar_df_name = os.path.join(base_dir, "output_data/features/all_features.csv")
ts_unsmoothed_df_name = os.path.join(base_dir, "output_data/time_series/unsmoothed_time_series.csv")
ts_smoothed_df_name = os.path.join(base_dir, "output_data/time_series/smoothed_time_series.csv")
ts_norm_df_name = os.path.join(base_dir, "output_data/time_series/norm_time_series.csv")

"""
FUNCTIONS
"""

"""
Helper function for normalizing data
"""
def normalize(lst):
    # Remove NaNs for the computation
    non_nan_lst = [x for x in lst if not math.isnan(x)]
    # Range of the data
    rnge = max(non_nan_lst) - min(non_nan_lst)
    # Normalized value is: (x - min) / (max - min)
    lst2 = [(x - min(non_nan_lst))/rnge for x in non_nan_lst]
    # Add the NaNs back in (assumes 2-backward, 2-forward smoothing)
    lst2 = [math.nan]*2 + lst2 + [math.nan]*2
    return lst2

"""
visualize_time_series() takes a DataFrame of time series and plots each column.

Inputs - a DataFrame with 'Year' as the first column and the time series in remaining columns
Outputs - nothing returned, Matplotlib graph shown
"""
def visualize_time_series(time_series_df):
    years = list(time_series_df['Year'])
    # Iterate through time series
    for col in list(time_series_df.columns)[1:]:
        data = list(time_series_df[col])
        plt.plot(years, data)
        plt.title(col)
        plt.show()

"""
full_tar_dataset() produces the full set of time series needed for the TAR analysis (see description at the top)
"""
def full_tar_dataset(visualize=True):
    # Read in the datasets
    non_idyom_features_df = pd.read_csv(non_idyom_filename)
    pic_df = pd.read_csv(pic_filename, sep='\s+', engine="python")
    ric_df = pd.read_csv(ric_filename, sep='\s+', engine="python")

    # Create 'ID' columns for the IDyOM features so we can merge properly
    pic_df['ID'] = pic_df['melody.name'].str[1:-1]
    ric_df['ID'] = ric_df['melody.name'].str[1:-1]

    # Get the columns we need from the IDyOM feature datasets
    pic_df = pic_df[['ID', 'mean.information.content']]
    ric_df = ric_df[['ID', 'mean.information.content']]
    pic_df.columns = ['ID', 'PIC']
    ric_df.columns = ['ID', 'RIC']

    # Merge these with the non_idyom_features DataFrame
    tar_df = pd.merge(non_idyom_features_df, pic_df, on="ID", how ='outer')
    tar_df = pd.merge(tar_df, ric_df, on="ID", how ='outer')

    # Save the full dataset before computing means by year
    tar_df.to_csv(full_tar_df_name, index=False)

    # Print the ranges of each feature (for Supplementary Materials)
    for feat in tar_df.columns:
        if feat == 'ID':
            continue
        if feat == 'Year':
            continue

        minimum = min(list(tar_df[feat]))
        maximum = max(list(tar_df[feat]))
        print("Range for", feat, ":", round(minimum, 3), "-", round(maximum, 3))

    # Before computing the time series, we need to exclude the values from 2023, since this will be our test set
    tar_df = tar_df[tar_df.Year != 2023]

    # Time series (non-smoothed)
    time_series_df = tar_df.groupby('Year').mean()
    time_series_df = time_series_df.reset_index(level=0)

    # Save the unsmoothed time series
    time_series_df.to_csv(ts_unsmoothed_df_name, index=False)

    # Prepare the data for smoothing by turning DataFrame into list of lists
    series_lists = []
    for column in list(time_series_df.columns[1:]):
        series_lists.append(list(time_series_df[column]))

    # Smooth the time series
    smoothed_lists = smoothing(series_lists)
    smoothed_lists = [list(time_series_df['Year'])] + smoothed_lists
    smoothed_lists = [list(i) for i in zip(*smoothed_lists)]
    smoothed_time_series_df = pd.DataFrame(smoothed_lists, columns = time_series_df.columns)

    # Save
    smoothed_time_series_df.to_csv(ts_smoothed_df_name, index=False)

    # Visualize each of the smoothed time series
    if visualize:
        visualize_time_series(smoothed_time_series_df)

    # Finally, normalize the time series
    norm_time_series_df = smoothed_time_series_df

    for col in norm_time_series_df.columns:
        if col == 'Year':
            continue
        else:
            norm_time_series_df[col] = normalize(list(norm_time_series_df[col]))

    # Save the normalized time series
    norm_time_series_df.to_csv(ts_norm_df_name, index=False)

"""
MAIN
"""
full_tar_dataset()
