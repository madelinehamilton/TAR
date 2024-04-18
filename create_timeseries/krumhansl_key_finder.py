from collections import deque
import scipy.stats as sps
import pretty_midi as pm
import pandas as pd
import os

"""
krumhansl_key_finder.py contains the functionality for computing the 'Tonal Strength' feature. It implements the key-finding
algorithm described in Krumhansl (1990).

key_finder() is the principal function.
"""

"""
midi_to_letter() converts a list of MIDI note numbers to letter notes (e.g., C, C#)
Inputs - list of MIDI note numbers
Outputs - list of strings representing letter notes
"""
def midi_to_letter(midi_note_lst):
    # MIDI note numbers cycle through C - B every 12 notes. Use the modulo operator
    # The remainder will determine which note the MIDI note number is
    remainders = [x % 12 for x in midi_note_lst]
    remainder_map = {0: 'C', 1: 'C#/Db', 2: 'D', 3: 'D#/Eb', 4: 'E', 5: 'F', 6: 'F#/Gb', 7: 'G', 8: 'G#/Ab', 9: 'A', 10: 'A#/Bb', 11: 'B'}
    return [remainder_map[x] for x in remainders]

"""
durational_vector() finds the durations (in seconds) that each of the 12 notes is played in a MIDI file
Inputs - a (monophonic) Pretty MIDI object
Outputs - 12-item list. First value gives the number of seconds C natural is played, second item gives the number of seconds
          C# is played, etc.
"""
def durational_vector(midi):
    # Get the duration and MIDI pitch number of each note event
    notes = midi.instruments[0].notes
    durations = [x.end - x.start for x in notes]
    pitches = [x.pitch for x in notes]
    # Convert MIDI pitch number to letters (D#, D, etc.)
    pitches_12 = midi_to_letter(pitches)
    # Initialize dictionary that tallies durations for each letter
    duration_tally = {'C':0, 'C#/Db': 0, 'D':0, 'D#/Eb':0, 'E':0, 'F':0, 'F#/Gb':0, 'G':0, 'G#/Ab':0, 'A':0, 'A#/Bb':0, 'B':0}
    # Iterate through the list of notes, tally the durations
    for i in range(len(pitches)):
        dur = durations[i]
        pitch = pitches_12[i]
        duration_tally[pitch] += dur
    return list(duration_tally.values())

"""
key_finder() estimates the key of a piece by correlating its durational vector with 24 different tone profiles
representing the 24 Western musical keys and selecting the key with the largest correlation coefficient.

Input - a (monophonic) Pretty MIDI object

Outputs - the correlation coefficient corresponding to the best-matching key.
"""

def key_finder(midi_obj):
    # Get the durational vector
    duration_vec = durational_vector(midi_obj)

    # C Major and Minor tone profiles
    major = deque([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor = deque([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

    # To start, correlate the durational vector with C Major and C Minor
    c_maj_coef, _ = sps.pearsonr(major, duration_vec)
    c_min_coef, _ = sps.pearsonr(minor, duration_vec)

    # Initialize lists to hold the correlation coefficients
    coefs_major = [c_maj_coef]
    coefs_minor = [c_min_coef]

    # Iterate through the tonics
    for i in range(11):
        # To get the new major tone profile, shift every value in the C Major tone profile one position to the right
        # The last item becomes the first item
        # Do the same for the C Minor tone profile
        major.rotate(1)
        minor.rotate(1)

        # Correlate the tone profile with the durational vector and store the result
        coefs_major.append(sps.pearsonr(major, duration_vec)[0])
        coefs_minor.append(sps.pearsonr(minor, duration_vec)[0])

    # Get the highest correlation coefficient among the major and minor keys separately
    max_maj, max_minor = max(coefs_major), max(coefs_minor)

    # Initialize best_index, which will hold the best-matching tonic, and best_val, the best correlation coefficient
    # Assume the best key is C Major for now
    best_index = 0
    best_val = max_maj
    mode = 'Major'

    # If the best major key correlation coef is higher than the best minor key correlation coef
    if max_maj >= max_minor:
        best_index = coefs_major.index(max_maj)
        
    # Otherwise, the best-matching key is minor
    else:
        best_index = coefs_minor.index(max_minor)
        best_val = max_minor
        mode = 'Minor'

    # Convert best_index to letter
    remainder_map = {0: 'C', 1: 'C#/Db', 2: 'D', 3: 'D#/Eb', 4: 'E', 5: 'F', 6: 'F#/Gb', 7: 'G', 8: 'G#/Ab', 9: 'A', 10: 'A#/Bb', 11: 'B'}
    tonic = remainder_map[best_index]
    key = tonic + " " + mode

    # If you need to see all keys and their correlation coefficients
    coefs_maj_w_keys = [0]*len(coefs_major)
    for i in range(len(coefs_major)):
        coef_tonic = remainder_map[i]
        coef_mode = 'Major'
        coef_key = coef_tonic + " " + coef_mode
        coefs_maj_w_keys[i] = (coefs_major[i], coef_key)

    coefs_min_w_keys = [0]*len(coefs_minor)
    for i in range(len(coefs_minor)):
        coef_tonic = remainder_map[i]
        coef_mode = 'Minor'
        coef_key = coef_tonic + " " + coef_mode
        coefs_min_w_keys[i] = (coefs_minor[i], coef_key)


    all_coefs = coefs_maj_w_keys + coefs_min_w_keys
    all_coefs = sorted(all_coefs, key=lambda x: x[0], reverse=True)
    # Print all_coefs if you want to display all keys and their correlation coefficients, sorted.
    # Return 'key' if you also want the predicted key
    return best_val
