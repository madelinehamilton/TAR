# Imports
import pandas as pd
import os
import pretty_midi as pm

"""
iso_prop.py contains the functionality for computing the Isochrony Proportion feature.

Inputs - a (monophonic) Pretty MIDI object
Outputs - isochrony proportion value
"""

def iso_proportion(midi_obj):
    # List of events in the melody
    notes = midi_obj.instruments[0].notes
    # First, we need to get the inter-onset intervals in the melody.
    # Instantiate IOI list
    iois = [0]*(len(notes) - 1)
    # Iterate through the notes, compute the IOI for each consecutive pair of onsets.
    for i in range(len(notes) - 1):
        # Current note
        current = notes[i]
        # Next note
        next = notes[i+1]
        # Compute IOI
        ioi = next.start - current.start
        # Store
        iois[i] = ioi

    # Now, iterate through the IOI pairs. Determine if each pair of IOIs are the same (within a small tolerance).
    iso_flags = [0]*(len(iois) - 1)
    for i in range(len(iois) - 1):
        current_ioi = iois[i]
        next_ioi = iois[i+1]

        # If the two IOIs are mostly equivalent (less than 1 millisecond apart), set the relevant flag to 1
        if abs(current_ioi - next_ioi) < 0.001:
            iso_flags[i] = 1

    # Count the number of equivalent IOI pairs
    iso_pairs = sum(iso_flags)
    # Divide by total number of pairs
    isochrony_fraction = iso_pairs / len(iso_flags)

    return isochrony_fraction
