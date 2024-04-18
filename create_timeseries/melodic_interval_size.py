# Imports
import pandas as pd
import os
import pretty_midi as pm

"""
mis() takes a Pretty MIDI object and computes the melodic interval size of the melody contained in it.
Melodic interval size is the average distance, in MIDI pitch note numbers, between consecutive pitch intervals.
For intervals which are one octave (12 semitones) or larger, the modulo 12 operator is applied.

Input: Pretty MIDI object (monophonic)
Output: melodic interval size of the melody
"""
def mis(midi_obj):

    # Note event list
    note_list = midi_obj.instruments[0].notes
    intervals = []

    # Iterate through each note event (except for the last one)
    for i in range(len(note_list)):
        if i == len(note_list)-1:
            continue
        else:
            # For each note event, get the pitch of the current note and the next note
            current_note = note_list[i]
            next_note = note_list[i+1]

            # Compute and store the melodic interval between the two notes
            interval = abs(current_note.pitch - next_note.pitch)
            # If the interval is large (octave or more), take modulo 12
            if interval > 11:
                interval = interval % 12

            intervals.append(interval)

    # Average the interval sizes
    mis = sum(intervals)/len(intervals)

    return mis
