Execute the following scripts in order:

1. Run autoregression_residuals.py first. This will fit autoregressive models on each feature, calculate everything needed for Table 2 in the paper, and saves the model residuals for linear regression. Output files will be in /output_data/reg_results/residuals/ and /output_data/reg_results/tables_for_paper/

2. Run residual_reg.py. It runs, per era, linear regression on the residuals from the autoregressive models. It calculates everything needed for Table 3 in the paper. Output files will be in /output_data/reg_results/tables_for_paper/

3. Run vector_autoregression.py, which fits VAR models to the (segmented) time series. NOTE: this script should be treated more like a Jupyter notebook; depending on the results you get at each step, you need to modify parts of the next step. Output files will be in /output_data/reg_results/VAR/

After you run these scripts, you can run:

- var_fits.py. This produces Figure 2 in the paper, which visualises the best VAR fits. If you want to visualise different VARs, you will need to manually edit the script. Output files will be in /output_data/visualizations/ 

- var_forecasts.py. This produces Figure S2 in the supplementary materials, which visualises the 2023 forecasts from the Era 3 VARs. It also produces Table 4 in the supplementary materials, which reports the forecasting errors of the Era 3 VAR. Output files will be in /output_data/visualizations/ and /output_data/reg_results/tables_for_paper/

The other files in the directory are:

- regression_helper.py, which contains helper functions for the autoregression and VAR modelling process.

- time_series_smoothing.py, which contains helper functions for time series smoothing.