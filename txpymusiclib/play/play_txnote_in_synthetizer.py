from beartype import beartype

from txpymusiclib.interval_package import txintervals
from txpymusiclib.play.play_floatfreqs_in_syntetizer import play_sequence_freqs
from txpymusiclib.scales_package.txnotecontainer import TxNoteContainer
from txpymusiclib.scales_package.txscales import TxScaleSt


@beartype
def play_sequence_notes(notes: TxNoteContainer, duration_secs: float):
    freqs = [note.get_freq() for note in notes.get_txnotes()]
    play_sequence_freqs(freqs, duration_secs)


@beartype
def play_scale_from_freq(freq: float, scale_semitone_intervals: TxScaleSt, duration_secons: float):
    freqs = list(txintervals.freqs_mult_accumulate(freq, scale_semitone_intervals.semitones))
    tail = list(reversed(freqs))[1:]
    print(freqs)
    play_sequence_freqs(freqs + tail, duration_secons)