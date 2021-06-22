#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for writing music in Python.

@author: khe
"""
from beartype import beartype
import numpy as np

from common.synt_wave.from_numpy_khe import get_sine_wave
from common.txtone import get_piano_notes
from common import sample_rates

DEFAULT_AMPLITUDE = 4096


@beartype
def apply_overtones(frequency: float, duration, factor, sample_rate=sample_rates.sample_rate_44100,
                    amplitude=DEFAULT_AMPLITUDE):
    '''
    Return fundamental note with overtones applied. 

    Parameters
    ----------
    frequency : float
        Frequency in hertz.
    duration : float
        Time in seconds.
    factor : list
        List of floats as fraction of the fundamental amplitude for amplitudes 
        of the overtones.
    sample_rate : int, optional
        Wav file sample rate. The default is 44100.
    amplitude : int, optional
        Peak Amplitude. The default is 4096.

    Returns
    -------
    fundamental : ndarray
        Output note of `float` type.

    '''
    assert abs(1 - sum(factor)) < 1e-8

    frequencies = np.minimum(np.array([frequency * (x + 1) for x in range(len(factor))]), sample_rate // 2)
    amplitudes = np.array([amplitude * x for x in factor])

    fundamental = get_sine_wave(frequencies[0], duration, sample_rate, amplitudes[0])
    for i in range(1, len(factor)):
        overtone = get_sine_wave(frequencies[i], duration, sample_rate, amplitudes[i])
        fundamental += overtone
    return fundamental


@beartype
def get_adsr_weights(frequency: float, duration, length, decay, sustain_level,
                     sample_rate=sample_rates.sample_rate_44100):
    '''
    ADSR(attack, decay, sustain, and release) envelop generator with exponential
    weights applied.

    Parameters
    ----------
    frequency : float
        Frequency in hertz.
    duration : float
        Time in seconds.
    length : list
        List of fractions that indicates length of each stage in ADSR.
    decay : list
        List of float for decay factor to be used in each stage for exponential
        weights. 
    sustain_level : float
        Amplitude of `S` stage as a fraction of max amplitude.
    sample_rate : int, optional
        Wav file sample rate. The default is 44100.

    Returns
    -------
    weights : ndarray

    '''
    assert abs(sum(length) - 1) < 1e-8
    assert len(length) == len(decay) == 4

    intervals = int(duration * frequency)
    len_A = np.maximum(int(intervals * length[0]), 1)
    len_D = np.maximum(int(intervals * length[1]), 1)
    len_S = np.maximum(int(intervals * length[2]), 1)
    len_R = np.maximum(int(intervals * length[3]), 1)

    decay_A = decay[0]
    decay_D = decay[1]
    decay_S = decay[2]
    decay_R = decay[3]

    A = 1 / np.array([(1 - decay_A) ** n for n in range(len_A)])
    A = A / np.nanmax(A)
    D = np.array([(1 - decay_D) ** n for n in range(len_D)])
    D = D * (1 - sustain_level) + sustain_level
    S = np.array([(1 - decay_S) ** n for n in range(len_S)])
    S = S * sustain_level
    R = np.array([(1 - decay_R) ** n for n in range(len_R)])
    R = R * S[-1]

    weights = np.concatenate((A, D, S, R))
    smoothing = np.array([0.1 * (1 - 0.1) ** n for n in range(5)])
    smoothing = smoothing / np.nansum(smoothing)
    weights = np.convolve(weights, smoothing, mode='same')

    weights = np.repeat(weights, int(sample_rate * duration / intervals))
    tail = int(sample_rate * duration - weights.shape[0])
    if tail > 0:
        weights = np.concatenate((weights, weights[-1] - weights[-1] / tail * np.arange(tail)))
    return weights


@beartype
def apply_pedal(note_values, bar_value: ( float,int)):
    '''
    Press and hold the sustain pedal throughout the bar.

    Parameters
    ----------
    note_values : list
        List of note duration.
    bar_value : float
        Duration of a measure in seconds.

    Returns
    -------
    new_values : list
        List of note duration with sustain.

    '''
    assert sum(note_values) % bar_value == 0
    new_values = []
    start = 0
    while True:
        cum_value = np.cumsum(np.array(note_values[start:]))
        end = np.where(cum_value == bar_value)[0][0]
        if end == 0:
            new_values += [note_values[start]]
        else:
            this_bar = np.array(note_values[start:start + end + 1])
            new_values += [bar_value - np.sum(this_bar[:i]) for i in range(len(this_bar))]
        start += end + 1
        if start == len(note_values):
            break
    return new_values


@beartype
def get_song_data(music_notes, note_values: list, bar_value, factor, length,
                  decay, sustain_level, sample_rate=sample_rates.sample_rate_44100, amplitude=DEFAULT_AMPLITUDE):
    '''
    Generate song from notes. 

    Parameters
    ----------
    music_notes : list
        List of note names. 
    note_values : list
        List of note duration.
    bar_value: float
        Duration of a bar. 
    factor : list
        Factor to be used to generate overtones.
    length : list
        Stage length to be used to calculate ADSR weights.
    decay : list
        Stage decay to be used to calculate ADSR weights.
    sustain_level : float
        Amplitude of `S` stage as a fraction of max amplitude.
    sample_rate : int, optional
        Wav file sample rate. The default is 44100.
    amplitude : int, optional
        Peak Amplitude. The default is 4096.

    Returns
    -------
    song : ndarray

    '''
    note_freqs = get_piano_notes()
    frequencies = [note_freqs[note] for note in music_notes]
    new_values = apply_pedal(note_values, bar_value)
    duration = int(sum(note_values) * sample_rate)
    end_idx = np.cumsum(np.array(note_values) * sample_rate).astype(int)
    start_idx = np.concatenate(([0], end_idx[:-1]))
    end_idx = np.array([start_idx[i] + new_values[i] * sample_rate for i in range(len(new_values))]).astype(int)

    song = np.zeros((duration,))
    for i in range(len(music_notes)):
        this_note = apply_overtones(frequencies[i], new_values[i], factor)
        weights = get_adsr_weights(frequencies[i], new_values[i], length,
                                   decay, sustain_level)
        song[start_idx[i]:end_idx[i]] += this_note * weights

    song = song * (amplitude / np.max(song))
    return song