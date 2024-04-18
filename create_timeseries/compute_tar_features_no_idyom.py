# Imports
from krumhansl_key_finder import key_finder
from pitch_standard_deviation import pitch_sd
from melodic_interval_size import mis
from onset_density import onset_density
from ti_od import tempo_invariant_onset_density
from iso_prop import iso_proportion
import pretty_midi as pm
import pandas as pd
import os

"""
compute_tar_features_no_idyom.py computes all features that do not require IDyOM. This includes the
Tonal Strength, Pitch SD, Melodic Interval Size, Onset Density, TI-OD, and ISO features.

Inputs
        - directory to the MIDI dataset
        - directory to the .csv containing manual per-melody metadata (this is necessary to compute TI-OD)

Outputs - a .csv with a DataFrame of these features is saved to /output_data/features

You need to specify the root directory.
"""

"""
DIRECTORIES
"""

# ROOT DIRECTORY
base_dir = "/Users/madelinehamilton/Documents/python_stuff/tar_repo/"

# MIDI directory
input_dir = os.path.join(base_dir, "midis")
# Per-melody metadata direcotry
melody_metadata_dir = os.path.join(base_dir, "metadata/per_mel_metadata.csv")
# Directory for output DataFrame
csv_name = os.path.join(base_dir, "output_data/features/non_idyom_features.csv")

"""
DATA PREPARATION
"""
# Read in the metadata
df = pd.read_csv(melody_metadata_dir)

"""
FUNCTIONS
"""

"""
compute_tar_features_no_idyom() does all the legwork here. It iterates through a directory of MIDIs, computes all
TAR features not involving IDyOM, and returns a DataFrame with the results.

Inputs:
    - directory of MIDI melodies
    - metadata with two columns: a 'Melody ID' column, which gives the melody's unique identifier, and a
      'Number of Bars' column, which gives the number of bars in the melody.

Outputs:
    - (returned) DataFrame with columns for ID, Year, Tonal_S, Pitch_SD, MIS, Onset_Density, TI_OD, ISO

"""
def compute_tar_features_no_idyom(directory, metadata):

    # Instantiate lists that will hold all the feature values. We'll turn it into a DataFrame at the end
    melody_ids = []
    years = []
    tonal_strengths = []
    pitch_sds = []
    mis_vals = []
    onset_densities = []
    ti_ods = []
    isos = []

    # Iterate through the MIDI directory
    for filename in os.listdir(directory):
        if filename.endswith(".mid"):
            # Read in MIDI file as a PrettyMidi object
            midi = pm.PrettyMIDI(os.path.join(directory, filename))
            # Melody ID is the filename minus ".mid"
            melody_id = filename[:-4]
            # The year is the first four characters of the filename
            year = int(filename[:4])

            # Compute features
            tonal_strength = key_finder(midi)
            sd = pitch_sd(midi)
            melodic_interval_size = mis(midi)
            od = onset_density(midi)
            ti_od = tempo_invariant_onset_density(midi, melody_id, metadata)
            iso_val = iso_proportion(midi)

            # Store information
            melody_ids.append(melody_id)
            years.append(year)
            tonal_strengths.append(tonal_strength)
            pitch_sds.append(sd)
            mis_vals.append(melodic_interval_size)
            onset_densities.append(od)
            ti_ods.append(ti_od)
            isos.append(iso_val)


    # Create DataFrame
    df_cols = ['ID', 'Year', 'Tonal_S', 'Pitch_SD', 'MIS', 'Onset_Density', 'TI_OD', 'ISO']
    df = pd.DataFrame(list(zip(melody_ids, years, tonal_strengths, pitch_sds, mis_vals, onset_densities, ti_ods, isos)), columns = df_cols)

    return df

"""
MAIN
"""
# Call function and save resulting DataFrame
output_df = compute_tar_features_no_idyom(input_dir, df)
output_df.to_csv(csv_name, index=False)
