import numpy as np
import pandas as pd

"""
regression_helper.py contains helper functions for the autoregressions, regressions, and vector autoregressions.
"""

# Z-score a list
def normalize(lst):
    rnge = max(lst) - min(lst)
    lst2 = [(x - min(lst))/rnge for x in lst]
    return lst2

# "Un-normalize" data
def un_normalize(orig, new):
    rnge = max(orig) - min(orig)
    un_norm = [(rnge*x + min(orig)) for x in new]
    return un_norm

# Root mean squared error between a list of original values and a list of fitted values
# This is normalized by the range of the original values
def nrmse_range(original_vals, model_vals):

    lst1 = original_vals
    lst2 = model_vals
    errors = [0]*(len(lst1) - 1)

    # Iterate through the two lists simultaneously
    for i in range(len(lst1)):
        if i == 0:
            continue
        else:
            x1 = lst1[i]
            x2 = lst2[i]
            # L2 error between the two values
            errors[i-1] = (x1-x2)**2

    # Take the mean and square root
    avg_error = (sum(errors)/len(errors))
    rmse = np.sqrt(avg_error)

    # Normalize by the range
    minimum = min(original_vals)
    maximum = max(original_vals)
    nmrse = rmse/(maximum-minimum)

    return nmrse

"""
compute_model_values() takes selected VAR coefficients, computes the fitted VAR values of features, and computes
the error between the model values and the actual feature values (nMRSE).

Again, statsmodels probably has a function that gives back the fitted values. I wanted to compute them manually
to study them (which didn't end up producing any meaningful insights because VAR coefficients are difficult to interpret).

Inputs:
        - a DataFrame with the original (normalized) time series
        - a DataFrame with VAR model coefficient data

Outputs:
        - a list of lists with
"""
def compute_model_values(ts_data, coef_data):
    # Get all dependent names
    dependent_names = list(coef_data['Dependent'].unique())
    # Dictionary to hold information
    fitted_values_dict = {}
    # Length of predictor data
    data_length = len(list(ts_data['RIC']))
    # Iterate through the dependents
    for i in range(len(dependent_names)):
        const = 0
        dependent_name = dependent_names[i]
        # Get the original time series
        ts = list(ts_data[dependent_name])
        # Get the coefficient data
        coefs = coef_data[coef_data['Dependent'] == dependent_name]
        # Which predictors do we have with this dependent?
        predictor_names = list(coefs['Predictor'].unique())
        # Iterate through all the predictors in this equation
        reg_values = []
        for i2 in range(len(predictor_names)):
            predictor = predictor_names[i2]
            coef_info = coefs[coefs['Predictor'] == predictor]
            # We might have multiple coefficients per predictor
            # Because of the different lags
            # So, iterate through the different lags of the same predictor
            for i3 in range(len(coef_info.index)):
                lag = list(coef_info['Lag'])[i3]
                coefficient = list(coef_info['Coefficient'])[i3]
                # For lag L, take off the last L elements, and add L nans to the beginning
                x_data = 0
                if lag == 0:
                    x_data = [1]*data_length
                else:
                    x_data = list(ts_data[predictor])
                lagged_x = [np.nan]*lag
                lagged_x = lagged_x + x_data[:len(x_data)-lag]
                # Multiply the lagged predictor by the coefficient
                lagged_x = [coefficient*x for x in lagged_x]
                reg_values.append(lagged_x)


        # reg_values is a list of lists. Each list corresponds to one relevant predictor
        # Each component list has the lagged values of the relevant time series multiplied by their appropriate coefficient
        # Add values together (add first value of each list, second value of each list, etc.)
        ys = list(map(sum, zip(*reg_values)))

        # Replace the first couple of nan values in the predicted value list with the original values
        # This is for nRMSE purposes. When a VAR (or AR) of lag L produces fitted values, it can't produce
        # The first L values. So we need to fill these in.
        nans = [0]*len(ys)
        for i in range(len(ys)):
            nans[i] = np.isnan(ys[i])
        number_of_nans = sum(nans)
        ys[:number_of_nans] = ts[:number_of_nans]

        # Error between the original and model values
        error = nrmse_range(ts, ys)
        # Store results
        fitted_values_dict[dependent_name] = (ts, ys, error)

    return fitted_values_dict
