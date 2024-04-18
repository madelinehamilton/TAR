# Trajectories and Revolutions in Western Popular Melody

This is the GitHub repository for the paper "Trajectories and Revolutions in Western Popular Melody" by Madeline Hamilton and Marcus Pearce. This repo includes the dataset used
for analysis (see github.com/madelinehamilton/BiMMuDa for the full dataset) as well as the scripts necessary for replicating the analysis.

Below is the outline for for replicating the TAR analysis. For each step, there is a more detailed README in the relevant directory.

1. Go into /create_timeseries/ and run compute_tar_features_no_idyom.py, compute the IDyOM features, and run produce_full_tar_dataset.py.

2. Go into /changepoint_detection/ and run python_changepoint_analysis.py, R_changepoint_analysis.R, tally_changepoints.py, visualize_changepoint_tallies.py, time_series_changepoint_visual.R, and time_series_legend.py.

3. Go into /regressions/ directory and run autoregression_residuals.py, residual_reg.py, vector_autoregression.py, var_fits.py, and var_forecasts.py.

In general, before executing every script, you need to specify the root directory. Additionally, if you name files differently, you'll need to edit the top portion of some scripts. Finally, some scripts require additional manual editing to conduct the analysis properly, so read the documentation of each script before trying to execute it.

The directories not mentioned above have the following purposes:

	- /metadata/ holds extra metadata needed to perform the analysis ("Number of Bars" feature)
        - /midis/ stores the dataset of MIDI melodies.
	- /output_data/ stores the outputs of the analysis, including time series data, visualizations, tables, etc. It contains several sub-directories that sort the output files.

# Dependencies

On the Python side, you'll need the standard data science libraries (os, pandas, matplotlib, seaborn, math, scipy, sklearn, statsmodels, and numpy), and some more niche 
libraries you may not have installed already (pretty_midi, json, collections, and ruptures)

On the R side, you need ggplot2 and ecp.
