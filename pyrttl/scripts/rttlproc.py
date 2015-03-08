import sys
import argh
from argh import arg

from pyrttl.rttl import rttl2score

import music21.midi.translate


def input2score(input):
    inputf = open(input) if input is not None else sys.stdin
    data = inputf.read()
    score = rttl2score(data)
    return score


@arg('-i', '--input', help='rttl input file')
def play(input=None):
    score = input2score(input)
    notes = list(score.parts[0].notes)
    print ' '.join(n.nameWithOctave for n in notes)
    score.show('midi')


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
    mf = music21.midi.translate.streamToMidiFile(score)
    mf.open(output, 'wb')
    mf.write()
    mf.close()


def main():
    parser = argh.ArghParser()
    parser.add_commands([play, dump, midi])
    parser.dispatch()


if __name__ == '__main__':
    main()
