# https://github.com/yuma-m/synthesizer
from txpymusiclib.note_package import txnote_khe_wrap
from txpymusiclib.play import play_floatfreqs_in_syntetizer

player, synthesizer_instance = play_floatfreqs_in_syntetizer.play_init()
play_floatfreqs_in_syntetizer.play_wave(player, synthesizer_instance, txnote_khe_wrap.note_A4.freq, 1.0)
