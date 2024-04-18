# Imports
import pandas as pd
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns

"""
visualize_changepoint_tallies.py produces Fig S1. in the supplementary materials. It requires the changepoint tally .csv
produced by tally_changepoints.py, which give the changepoints for each feature found by changepoint detection and
their tallies.

You need to specify the root directory.

Input: changepoint tally .csv produced by tally_changepoints.py, which give the changepoints for each feature found by changepoint detection and their tallies.
Output: A .png with Figure S1.
"""

"""
DIRECTORIES
"""

# SPECIFY ROOT DIRECTORY
base_dir = "/Users/madelinehamilton/Documents/python_stuff/tar_repo/"

# Changepoint tally directory
changepoint_tally_filename = os.path.join(base_dir, "output_data/changepoints/aggregated_changepoint_tallies.csv")

# Output directory for visualization
figure_filename = os.path.join(base_dir, "output_data/visualizations/aggregated_changepoint_tallies.png")

"""
HELPER FUNCTIONS
"""

"""
get_full_tallies takes changepoint position + tally lists and adds in all possible positions, with corresponding tallies
of 0.

Example: position list [1977, 2000, 2010] with tally list [33, 48, 60]
--> [1952, 1953, ... 1977, 1978, ... 2000, ... 2010 ... 2019] with tally list [0, 0, ... 33, 0, ... 48, ..., 60, ... 0]

Input: list of positions of the changepoints, in years, and its tally list of the same length, giving the tally of each
       changepoint.
Output: modified position and tally lists (see example)
"""
def get_full_tallies(positions, non_zero_tallies):

    # Initialize dictionary of tallies: {1952: 0, 1953: 0, ... 2020: 0}
    full_pos = list(range(1952, 2021))
    tallies = [0]*69
    tally_dict = dict(zip(full_pos, tallies))

    # Iterate through the input positions list, updating the tally dictionary by filling in the non-zero tallies
    for i in range(len(positions)):
        tally_dict[positions[i]] = non_zero_tallies[i]

    keys = list(tally_dict.keys())
    values = list(tally_dict.values())
    return keys, values

"""
tally_visualization() produces Figure S1 and saves it as a .png

Inputs:
    - name of the file with the changepoint tallies
    - desired directory of the visualization
    - changepoint tally threshold
Outputs:
    - Nothing returned, .png with visual saved
"""
def tally_visualization(filename, viz_filename, thres):

    threshold = thres

    # Read in changepoint tally DataFrame, get the full tallies for each feature
    df = pd.read_csv(filename)

    feat_list = list(df['Feature'])
    tally_list = [0]*len(feat_list)
    features = dict(zip(feat_list, tally_list))
    for f in features.keys():
        row = df.loc[df['Feature'] == f]
        positions = json.loads(list(row['Positions'])[0])
        tallies = json.loads(list(row['Tallies'])[0])
        _, full_tallies = get_full_tallies(positions, tallies)
        features[f] = full_tallies

    # Matplotlib/sns settings
    plt.style.use('default')
    plt.rcParams['figure.dpi'] = 600
    plt.rcParams['savefig.dpi'] = 600
    plt.rcParams['font.family'] = "Arial"
    plt.rcParams['font.size'] = 8
    plt.rcParams['legend.fontsize'] = 9
    sns.set_context('paper', font_scale=0.9)

    # "years" will be the x axis for every subplot
    # "ys" are the y ticks we want
    years = list(range(1952, 2021))
    ys = list(np.arange(0, 241, 40))

    # Initialize figure; grid with 3 rows 3 columns
    fig = plt.figure(constrained_layout=True)
    gs = GridSpec(3, 3, figure=fig)

    # Tonal Strength
    ax0 = fig.add_subplot(gs[0, :1])
    ax0.plot(years, features['Tonal_S'])
    ax0.axhline(y=threshold, color='r', linestyle='-')
    ax0.set_yticks(ys)
    ax0.set_yticklabels(ys)
    ax0.set_xlabel('Year')
    ax0.set_ylabel('Changepoint Tally')
    ax0.title.set_text("Tonal S.")

    # PIC
    ax1 = fig.add_subplot(gs[0, 1:2])
    ax1.plot(years, features['PIC'])
    ax1.axhline(y=threshold, color='r', linestyle='-')
    ax1.set_yticks(ys)
    ax1.set_yticklabels(ys)
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Changepoint Tally')
    ax1.title.set_text("PIC")

    # Pitch SD
    ax2 = fig.add_subplot(gs[0, 2:3])
    ax2.plot(years, features['Pitch_SD'])
    ax2.axhline(y=threshold, color='r', linestyle='-')
    ax2.set_yticks(ys)
    ax2.set_yticklabels(ys)
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Changepoint Tally')
    ax2.title.set_text("Pitch SD")

    # MIS
    ax3 = fig.add_subplot(gs[1, :1])
    ax3.plot(years, features['MIS'])
    ax3.axhline(y=threshold, color='r', linestyle='-')
    ax3.set_yticks(ys)
    ax3.set_yticklabels(ys)
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Changepoint Tally')
    ax3.title.set_text("MIS")

    # Onset Density
    ax4 = fig.add_subplot(gs[1, 1:2])
    ax4.plot(years, features['Onset_Density'])
    ax4.axhline(y=threshold, color='r', linestyle='-')
    ax4.set_yticks(ys)
    ax4.set_yticklabels(ys)
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Changepoint Tally')
    ax4.title.set_text("Onset Density")

    # TI-OD
    ax4 = fig.add_subplot(gs[1, 2:3])
    ax4.plot(years, features['TI_OD'])
    ax4.axhline(y=threshold, color='r', linestyle='-')
    ax4.set_yticks(ys)
    ax4.set_yticklabels(ys)
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Changepoint Tally')
    ax4.title.set_text("TI-OD")

    # ISO
    ax5 = fig.add_subplot(gs[2, :1])
    ax5.plot(years, features['ISO'])
    ax5.axhline(y=threshold, color='r', linestyle='-')
    ax5.set_yticks(ys)
    ax5.set_yticklabels(ys)
    ax5.set_xlabel('Year')
    ax5.set_ylabel('Changepoint Tally')
    ax5.title.set_text("ISO")

    # RIC
    ax6 = fig.add_subplot(gs[2, 1:2])
    ax6.plot(years, features['RIC'])
    ax6.axhline(y=threshold, color='r', linestyle='-')
    ax6.set_yticks(ys)
    ax6.set_yticklabels(ys)
    ax6.set_xlabel('Year')
    ax6.set_ylabel('Changepoint Tally')
    ax6.title.set_text("RIC")

    # Multivariate
    ax7 = fig.add_subplot(gs[2, 2:3])
    ax7.plot(years, features['Multivariate'])
    ax7.axhline(y=threshold, color='r', linestyle='-')
    ax7.set_yticks(ys)
    ax7.set_yticklabels(ys)
    ax7.set_xlabel('Year')
    ax7.set_ylabel('Changepoint Tally')
    ax7.title.set_text("Multivariate")

    # Title of entire figure
    fig.suptitle("Changepoint Tallies")

    # Save
    plt.savefig(viz_filename, bbox_inches='tight')

# Call function
tally_visualization(changepoint_tally_filename, figure_filename, 120)
