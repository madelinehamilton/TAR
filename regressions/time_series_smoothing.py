import numpy as  np

"""
time_series_smoothing.py contains functionality for mean-smoothing time series. In the DOM analysis, I use 2-forward 2-back
mean smoothing.

Inputs - a list of lists, where each list is a time series to be smoothed
Outputs - a list of lists, where each list is a smoothed time series
"""

# Mean smoothing window function. Returns a list of weights
"""
average() is a mean smoothing window function. Consider a data point at index x, with a smoothing window (x-backward) to
(x+forward) (inclusive). Here we simply take the average of all data points in this window, so the weights we return are
all equal.
"""
def average(backward, forward):
    length = 1 + forward + backward
    return [1]*length

"""
smoothing() takes a list of lists and smooths each one
"""
def smoothing(lists, forward=2, backward=2):

    # Starting and stopping indices
    start_index = backward
    end_index = len(lists[0]) - forward - 1

    # Smoothed data
    smoothed_lists = []

    # Smoothing weights
    smoothing_func = average(backward, forward)

    for lst in lists:
        new_lst = [np.nan]*len(lst)
        for i in range(start_index, end_index+1):
            # Get all relevant values
            rel_vals = lst[i-backward:i+forward+1]
            # Multiply by smoothing weights and sum
            smoothed = sum([a*b for a,b in zip(rel_vals,smoothing_func)])/sum(smoothing_func)
            new_lst[i] = smoothed
        smoothed_lists.append(new_lst)

    return smoothed_lists
