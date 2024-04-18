# Imports
import os
import pretty_midi as pm
import pandas as pd
import numpy as np

"""
pitch_sd() takes a Pretty MIDI object and computes the pitch standard deviation of the melody it contains.
This is done by removing all temporal information, i.e., obtaining a list of MIDI pitches for each note event, and
taking the standard deviation of the list.

Inputs - a (monophonic) Pretty MIDI object
Outputs - pitch standard deviation of the melody
"""
def pitch_sd(midi_obj):
    # List of MIDI pitch numbers for each note vent
    notes = midi_obj.instruments[0].notes
    pitches = [x.pitch for x in notes]
    # Compute the standard deviation of this list
    sd = np.std(pitches)
    return sd
