import sys
import os

from tempfile import NamedTemporaryFile

import logging
logging.basicConfig()
logger = logging.getLogger('rttlproc')

import argh
from argh import arg

from pyrttl.rttl import rttl2score, score2midi, get_degree

import music21 as m21

try:
    import mido
    from mido import MidiFile
    MIDI_PLAY_SUPPORT = True
except ImportError:
    MIDI_PLAY_SUPPORT = False


def input2score(input):
    inputf = open(input) if input is not None else sys.stdin
    data = inputf.read()
    score = rttl2score(data)
    return score


def score2midifile(score):
    midif = NamedTemporaryFile('wb', delete=False)
    score2midi(score, midif.name)
    midif.close()
    mf = MidiFile(midif.name)
    return mf


@arg('-i', '--input', help='rttl input file')
@arg('-p', '--port', help='midi output port')
def play(input=None, port='fluidsynth'):
    if not MIDI_PLAY_SUPPORT:
        logger.error('Midi player not enabled. Install mido library first')
        sys.exit(1)

    score = input2score(input)
    mf = score2midifile(score)

    midi_out = mido.open_output(port)

    key = score.analyze('key')
    print key

    for message in mf.play():
        midi_out.send(message)
        if message.type == 'note_on':
            midi_pitch = message.note
            pitch = m21.pitch.Pitch(midi_pitch)
            degree = get_degree(key, pitch)
            print pitch, degree
    os.remove(mf.filename)



@arg('-i', '--input', help='rttl input file')
def dump(input=None):
    score = input2score(input)
    notes = list(score.parts[0].notes)
    metronome = score.metronomeMarkBoundaries()[0][2]
    print '%2.f BPM' % metronome.getQuarterBPM()
    print ' '.join(n.nameWithOctave for n in notes)


@arg('-i', '--input', help='rttl input file')
@arg('-o', '--output', help='midi output file')
def midi(input=None, output=None):
    score = input2score(input)
    score2midi(score, output)


def main():
    parser = argh.ArghParser()
    parser.add_commands([play, dump, midi])
    parser.dispatch()


if __name__ == '__main__':
    main()
