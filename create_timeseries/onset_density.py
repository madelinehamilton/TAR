# Imports
import os
import pretty_midi as pm
import pandas as pd

"""
onset_density() computes the onset density of a monophonic MIDI object.
Onset density is the average number of note events per second.

Input: a Pretty MIDI object
Output: the onset density of the melody contained in the MIDI
"""
def onset_density(midi_obj):
    # Length of melody in seconds
    length =  midi_obj.instruments[0].notes[-1].end
    # Number of notes
    num_notes = len(midi_obj.instruments[0].notes)
    return (num_notes/length)
