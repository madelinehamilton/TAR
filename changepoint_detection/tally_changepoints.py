# Imports
import pandas as pd
import os
import numpy as np
import collections

"""
tally_changepoints.py tallies the changepoints from the four changepoint methods and aggregates the tallies based on
the rules specified in the supplementary materials.

Inputs
        - directory of the changepoints from the R method (top-down)
        - directory of the changepoints from the Python methods (window-sliding, bottom-up, PELT)
Outputs
        - .csv with the raw changepoint tallies (non-aggregated)
        - .csv with the aggregated changepoint tallies

You need to specify the root directory.
"""

"""
DIRECTORIES
"""
# SPECIFY BASE DIRECTORY
base_dir = "/Users/madelinehamilton/Documents/python_stuff/tar_repo/"

# R changepoints
r_changepoints_table_name = os.path.join(base_dir, "output_data/changepoints/r_changepoints.csv")
# Python changepoints
python_changepoints_table_name = os.path.join(base_dir, "output_data/changepoints/python_changepoints.csv")
# Output un-processed changepoint tally .csv
tally_csv_name = os.path.join(base_dir, "output_data/changepoints/changepoint_tallies.csv")
# Output processed/aggregated tallies
processed_tally_csv_name = os.path.join(base_dir, "output_data/changepoints/aggregated_changepoint_tallies.csv")

"""
DATA PREPARATION
"""

# Read in and prepare the R changepoints (top-down method)
r_changept_df = pd.read_csv(r_changepoints_table_name, names=["feature", "alpha", "k", "min_size", "pos"], header=None)
r_changept_df = r_changept_df.iloc[1:]
r_changept_df['k'] = r_changept_df['k'].fillna("NULL")
r_changept_df = r_changept_df[["feature", "k", "min_size", "pos"]]

# Read in and prepare the Python changepoints (PELT, window-sliding, bottom-up)
python_changept_df = pd.read_csv(python_changepoints_table_name, names=["feature", "method", "cost", "k", "min_size", "penalty", "win_size", "pos"], header=None)
python_changept_df = python_changept_df.iloc[1:]
python_changept_df = python_changept_df[["feature", "k", "min_size", "pos"]]

# Combine the two tables to create the full changepoint DataFrame
full_table = pd.concat([r_changept_df, python_changept_df], ignore_index=True)

"""
TALLY CHANGEPOINTS
"""

def tally_changepoints(changept_df):

    # For each feature, tally the changepoints
    tallies = changept_df.groupby(['feature'])['pos'].value_counts()
    tally_df = pd.DataFrame(columns=['Feature','Positions','Tallies'])
    features = list(set([x[0] for x in list(tallies.index)]))

    # How to I turn this into a useful DataFrame? I guess I have to go the long way
    for f in features:
        counts = tallies[f]
        positions = [int(x) for x in list(counts.index)]
        tals = list(counts.values)
        # Convert from time series position to years
        positions = [1951 + x for x in positions]

        # We don't need the changepoints at 2020. Remove them
        if 2020 in positions:
            cpt_index = positions.index(2020)
            keep_indexes = [x for x in range(len(positions)) if x != cpt_index]
            positions = list(np.array(positions)[keep_indexes])
            tals = list(np.array(tals)[keep_indexes])

        # We should sort the positions so that they're ascending by year
        # This makes it easier to read when you inspect the tallies manually
        tuples = [(positions[i], tals[i]) for i in range(len(positions))]
        tuples.sort()
        positions = [x[0] for x in tuples]
        tals = [x[1] for x in tuples]

        dict_for_df = {'Feature': f, 'Positions': positions, 'Tallies': tals}
        tally_df = tally_df.append(dict_for_df, ignore_index=True)

    return tally_df

# Full table (R + Python)
full_tally_df = tally_changepoints(full_table)

# Write out the unprocessed tallies
full_tally_df.to_csv(tally_csv_name, index=False)

"""
AGGREGATE TALLIES
"""

"""
Rules:

We will allow aggregation if the years are:
    - Consecutive (i.e., 1976 and 1977)
    - Two years apart (i.e., 1961 and 1963)

We will sum tallies this way:
    - Two consecutive years: aggregate into the earlier year [2000, 2001] --> 2000
    - Three consecutive years: aggreagate into the median year [2006, 2007, 2008] --> 2007
    - Two years two years apart: aggregate into the mean year [1961, 1963] --> 1962

The purpose of this is to simplify the output a bit, so the true changepoints and eras become clear.
"""

"""
Helper functions
"""
"""
check_cons_years() takes an index for a list of time positions (years) and checks if the next time position is only
one year apart from the time position at the index. If it is, it aggregates the respective tallies into the tally
for the earlier year.

Inputs -
        - List of time positions
        - List of changepoint tallies for each time position
        - Index of the time position list the function is supposed to check

Outputs -
        - The new list of tallies
        - A flag (True/False) indicating if the new list of tallies is different from the inputted list.
"""
def check_cons_years(pos_list, tally_list, index):

    # Get the relevant year and the year at the next index
    pos = pos_list[index]
    next_pos = pos_list[index+1]

    # Flag that indicates if changes were made
    change_flag = False

    # Check if the years are consecutive
    if (next_pos - pos) == 1:
        change_flag = True
        # Tallies go into the earlier year
        tally_list[index] = tally_list[index] + tally_list[index+1]
        # Set the later year's tally to 0
        tally_list[index+1] = 0

    return tally_list, change_flag

"""
check_three_cons_years() takes an index for a list of time positions (years) and checks if the next two time positions
are only one and two years apart from time position at the index. That is, the function checks if the current index
and the next two indices point to three consecutive years. If they do, the function then aggregates the tallies into the
median year.

Inputs -
        - List of time positions
        - List of changepoint tallies for each time position
        - Index of the time position list the function is supposed to check

Outputs -
        - The new list of tallies
        - A flag (True/False) indicating if the new list of tallies is different from the inputted list.
"""
def check_three_cons_years(pos_list, tally_list, index):

    # Get the relevant year and the years at the next two indices
    pos = pos_list[index]
    next_pos = pos_list[index+1]
    next_pos_2 = pos_list[index+2]

    # Flag that indicates if changes were made
    change_flag = False

    # Check if the years are consecutive
    if (next_pos - pos) == 1:
        if (next_pos_2 - next_pos) == 1:
            change_flag = True
            # Tallies go into the median year
            tally_list[index+1] = tally_list[index] + tally_list[index+1] + tally_list[index+2]
            # Set the other two tallies to 0
            tally_list[index] = 0
            tally_list[index+2] = 0

    return tally_list, change_flag

"""
check_two_years_apart() takes an index for a list of time positions (years) and checks if the next time position
is only two years later than the time position at the index. If it is, the function then adds a new time position
into the position list (the mean year between the two time positions) and aggregates the tallies into the
median year.

Inputs -
        - List of time positions
        - List of changepoint tallies for each time position
        - Index of the time position list the function is supposed to check

Outputs -
        - The new time position list
        - The new list of tallies
        - A flag (True/False) indicating if the new list of tallies is different from the inputted list.
"""
def check_two_years_apart(pos_list, tally_list, index):

    # Get the relevant year and the year at the next index
    pos = pos_list[index]
    next_pos = pos_list[index+1]

    # Flag that indicates if we're going to make changes
    change_flag = False

    # Check if the years are two years apart
    if (next_pos - pos) == 2:
        change_flag = True
        # Tallies go into the earlier year
        tally_list[i] = tally_list[index] + tally_list[index+1]
        # Set the later year's tally to 0
        tally_list[index+1] = 0
        # Add 1 year to the changepoint position year
        pos_list[index] = pos_list[index] + 1

    return pos_list, tally_list, flag

"""
Iterate through the features and aggregate the changepoints
"""

# Instantiate DataFrame that will store the results
aggregated_tally_df = pd.DataFrame(columns=['Feature','Positions','Tallies'])
# List of features to iterate through
feat_list = list(full_tally_df['Feature'])

# Iterate through the features
for feat in feat_list:
    # Get the relevant data: the lists of time positions and changepoint tallies for the feature.
    feat_dat = full_tally_df.loc[full_tally_df['Feature'].isin([feat])]
    cpt_positions = list(feat_dat['Positions'])[0]
    cpt_tallies = list(feat_dat['Tallies'])[0]

    # Instantiate a "skip list", to skip over positions if we need to
    skip_list = [False]*len(cpt_positions)

    # Iterate through the time positions
    for i in range(len(cpt_positions)):
        pos = cpt_positions[i]
        skip_flag = skip_list[i]

        # If skip value is False
        if not skip_flag:
            # Check if we can look at i+1 and i+2 without running into an index error
            if (len(cpt_positions) - i) > 2:
                # In this condition, we can look at both i+1 and i+2
                # Check for three consecutive years
                cpt_tallies, flag = check_three_cons_years(cpt_positions, cpt_tallies, i)
                # If there are three consecutive years, change the skip flags
                if flag:
                    skip_list[i+1] = True
                    skip_list[i+2] = True
                # If we didn't find three consecutive years, check for 2 consecutive years
                else:
                    cpt_tallies, flag = check_cons_years(cpt_positions, cpt_tallies, i)
                    # If there are two consecutive years, change the next skip flag
                    if flag:
                        skip_list[i+1] = True
                    # If the flag is still False, check for two years apart
                    else:
                        cpt_positions, cpt_tallies, flag = check_two_years_apart(cpt_positions, cpt_tallies, i)
                        # If flag is True, change the next skip flag
                        if flag:
                            skip_list[i+1] = True
                        else:
                            continue

    # Print out which "true" changepoints (the changepoints with tallies that exceed the threshold) the feature has
    true_cpts = []
    for i in range(len(cpt_positions)):
        pos = cpt_positions[i]
        tally = cpt_tallies[i]
        if tally >= 120:
            true_cpts.append(pos)

    print("List of changepoints for", feat, ":", true_cpts)
    print()

    # Store results for DataFrame
    dict_for_df = {'Feature': feat, 'Positions': cpt_positions, 'Tallies': cpt_tallies}
    aggregated_tally_df = aggregated_tally_df.append(dict_for_df, ignore_index=True)

"""
Write out the aggregated tallies, which will be used for visualization and analysis
"""
aggregated_tally_df.to_csv(processed_tally_csv_name, index=False)
