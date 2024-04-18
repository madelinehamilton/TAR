Run the following scripts in order:

1. Run python_changepoint_analysis.py. and R_changepoint_analysis.R This will compute the changepoints according four changepoint methods. Python is used for three of the methods, and R is used for one of the methods. Output files will be in /output_data/changepoints/

2. Tally up the changepoints with tally_changepoints.py. This will count how many times each year was considered a changepoint, among all four of the methods. Aggregation of tallies is done according to the rules described in the supplementary materials. Output files will be in /output_data/changepoints/

After you run these scripts, you can execute any of these scripts in any order:

- visualize_changepoint_tallies.py creates Figure S1 in the paper. The .png will be in /output_data/visualizations/

- time_series_changepoint_visual.R creates separate figures for each time series with their respective changepoints, which are used to create Figure 1. NOTE: you will need to specify the changepoints for each feature manually. Additionally, Figure 1 in the paper was created with Google Slides, to combine the individual plots and add the shaded boxes representing the revolutions. Output images will be in /output_data/visualizations/timeseries_w_changepoints/

- time_series_legend.py creates the legend for Figure 1. The time series plot is included in the resulting figure; screenshot only the legend (apologies for the messiness). The output image will be in /output_data/visualizations/timeseries_w_changepoints/

- per_era_averages.py computes feature averages per era (if you get different changepoints, you will need to manually edit this file so the eras are defined properly). Output is printed. 
