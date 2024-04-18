import numpy as  np

"""
time_series_smoothing.py contains functionality for mean-smoothing time series. In the TAR analysis, 2-forward 2-back
mean smoothing is used, so for a data point at time position t, the smoothed time series point is an average of
the values at t-2, t-2, t, t+1 and t+2.

Inputs - a list of lists, where each list is a time series to be smoothed
Outputs - a list of lists, where each list is a smoothed time series
"""

"""
average() helps with mean smoothing. Consider a data point at index x, with a smoothing window
[x - backward, x + forward]. When simply taking the average of all data points in this window, all points in the window
are weighted equally, so it returns a list of 1's of length 1 + backward + forward.
"""
def average(backward, forward):
    length = 1 + forward + backward
    return [1]*length

"""
smoothing() takes a list of lists and smooths each one
"""
def smoothing(lists, forward=2, backward=2):

    # Starting and stopping indices for the smoothing window
    start_index = backward
    end_index = len(lists[0]) - forward - 1

    # Insantiate lists of smoothed data
    smoothed_lists = []

    # Smoothing weights
    smoothing_func = average(backward, forward)

    # Iterate through each time series to be smoothed
    for lst in lists:
        # Instantiate smoothed time series
        new_lst = [np.nan]*len(lst)
        # Slide the window through the list
        for i in range(start_index, end_index+1):
            # Get values from window
            rel_vals = lst[i-backward:i+forward+1]
            # Multiply by smoothing weights and sum
            # (we're just averaging here, but I write it this way in case I need to use a more sophisticated smoothing function)
            smoothed = sum([a*b for a,b in zip(rel_vals,smoothing_func)])/sum(smoothing_func)
            new_lst[i] = smoothed
        # Store the new smoothed time series
        smoothed_lists.append(new_lst)

    return smoothed_lists
