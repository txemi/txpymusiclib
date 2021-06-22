import common.play
import common.txchord
from beartype import beartype
from synthesizer import Player, Synthesizer, Waveform

from common.txchord import mingusChord2Notes
from common.txtone import get_piano_notes


@beartype
def play_init():
    player = Player()
    player.open_stream()
    synthesizer_instance = Synthesizer(osc1_waveform=Waveform.sine, osc1_volume=1.0, use_osc2=False)
    return player, synthesizer_instance


@beartype
def play_wave(player: Player, synthesizer_instance: Synthesizer, freq, duration):
    wave_A4 = synthesizer_instance.generate_constant_wave(freq, duration)
    player.play_wave(wave_A4)


@beartype
def play_sequence(notes):
    player, synthesizer_instance = play_init()
    note2freq = get_piano_notes()
    for note in notes:
        freq = note2freq[note]
        play_wave(player, synthesizer_instance, freq, 1.0)


@beartype
def play_chord_from_freqs(player1: Player, synthesizer1: Synthesizer, freqs, duration):
    chord_wave = synthesizer1.generate_chord(freqs, duration)
    player1.play_wave(chord_wave)


@beartype
def play_chord_from_freq_and_chord(player1: Player, synthesizer1: Synthesizer, freq, chord, duration):
    freqs = list(common.txchord.TxChord.freqs_mult(freq, chord))
    play_chord_from_freqs(player1, synthesizer1, freqs, duration)


@beartype
def play_chord_from_symbolic(player: Player, synthesizer_instance: Synthesizer, chords, duration):
    chord_wave = synthesizer_instance.generate_chord(chords, duration)
    player.play_wave(chord_wave)


@beartype
def play_chord_chord_notation(player: Player, synthesizer_instance: Synthesizer, current_chord_name):
    chord_notes = mingusChord2Notes(current_chord_name)
    play_chord_from_symbolic(player, synthesizer_instance, chord_notes, 1.0)


@beartype
def play_chords_chord_notation(player: Player, synthesizer_instance: Synthesizer, chordseq: (list, tuple)):
    for current_chord_name in chordseq:
        play_chord_chord_notation(player, synthesizer_instance, current_chord_name)


@beartype
def play_chords_loop_chord_notation(chordseq: (list, tuple), times: int):
    player, synt = play_init()
    for i in range(times):
        play_chords_chord_notation(player, synt, chordseq)
