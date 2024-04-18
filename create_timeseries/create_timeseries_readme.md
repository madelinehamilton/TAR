Run the following scripts in order:

1. Run compute_tar_features_no_idyom.py to compute the features that do not require IDyOM, specifying the base directory in the file beforehand. Output files will be in /output_data/features/

2. Compute the IDyOM features (see idyom_feature_instructions.txt). Put the resulting two .dat files in /output_data/features/.

3. Run produce_full_tar_dataset.py, specifying the base directory and the names of the .dat IDyOM files beforehand. Output files will be in /output_data/features and /output_data/time_series/

The other scripts in the directory are:

	- scripts that define functions which compute 6 and of 8 TAR features: "krumhansl_key_finder.py", "pitch_standard_deviation.py", "melodic_interval_size.py", "onset_density.py, "ti_od.py" and "iso_prop.py".
	- "time_series_smoothing.py" defines helper functions for time series smoothing. 
