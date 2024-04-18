# Imports
import os
import pretty_midi as pm
import pandas as pd

"""
ti_od.py computes the tempo-invariant onset density (TI-OD) of a monophonic Pretty MIDI MIDI object.
TI-OD is the average number of note events per bar (measure).

Inputs:
        - a Pretty MIDI object
        - the ID of the melody
        - a DataFrame containing the manual per-melody metadata so the number of bars in the melody is accessible

Output: the onset density of the melody contained in the MIDI
"""

def tempo_invariant_onset_density(midi_obj, id, df):
    # Number of notes
    num_notes = len(midi_obj.instruments[0].notes)
    # Get the "Number of Bars" corresponding to the melody ID
    num_bars = list(df.loc[df['Melody ID'].isin([id])]['Number of Bars'])[0]
    return (num_notes/num_bars)
