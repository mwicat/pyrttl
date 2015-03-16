from pyparsing import *
import music21 as m21
import string


name = Word(string.printable.replace(':', ''))

control_name = oneOf('o d b')
control_value = Word(nums).setParseAction(lambda x: int(x[0]))
control_pair = Group(control_name + Suppress('=') + control_value + Suppress(Optional(',')))
control_section = OneOrMore(control_pair)
control_section.setParseAction(lambda x: dict(list(x)))

duration = oneOf('1 2 4 8 16 32').setParseAction(lambda x: int(x[0]))
pitch = oneOf('P C C# D D# E F F# G G# A A# B', caseless=True)
scale = oneOf('4 5 6 7')
special_duration = '.'


def parseNote(x):
    d = 4. / x['duration'] if 'duration' in x else None
    dots = 1 if x.get('special-duration') else 0
    if x['pitch'].lower() == 'p':
        note = m21.note.Rest(quarterLength=d, dots=dots)
    else:
        octave = x.get('scale', '')
        if octave:
            octave = int(octave) - 1
        name = '%s%s' % (x['pitch'], octave)
        note = m21.note.Note(name, quarterLength=d, dots=dots)
    return note

note = Optional(duration).setResultsName('duration') + \
             pitch.setResultsName('pitch') + \
             Optional(scale).setResultsName('scale') + Optional(special_duration).setResultsName('special-duration') + \
             Suppress(Optional(','))
note.setParseAction(parseNote)

tone_commands = Group(OneOrMore(note))

rtx = name + Suppress(':') + control_section + Suppress(':') + tone_commands

s = 'IndianaTheme:d=4,o=5,b=225:e,16f,8g,2c6,d,16e,1f,g,16a,8b,2f6,a,16b,c6,d6,e6,e,16f,8g,1c6,d6,16e6,2f6,g,16g,e6,d6,16g,e6,d6,16g,f6,e6,16d6,2c6'


def parse_rttl(s):
    s = s.strip().replace('_', '#')
    title, control_section, tone_commands = rtx.parseString(s)
    rttl_dict = {'title': title,
                'control_section': control_section,
                'tone_commands': tone_commands}
    return rttl_dict


def rttl2score(rttl_data, analyze_key=True):
    rttl_dict = parse_rttl(rttl_data)
    title = rttl_dict['title']
    control_section = rttl_dict['control_section']
    tone_commands = rttl_dict['tone_commands']

    score = m21.stream.Score()
    score.metadata = m21.metadata.Metadata(title=title, composer='')

    tm = m21.tempo.MetronomeMark(number=control_section['b'])
    score.append(tm)

    part = m21.stream.Part()
    score.append(part)

    for note in tone_commands:
        if not note.isRest and note.octave is None:
            note.octave = control_section['o'] - 1
        if note.quarterLength is None:
            note.quarterLength = 4. / control_section['d']
        part.append(note)

    if analyze_key:
        key = part.analyze('key')
        part.insert(0, key)

    return score


def score2midi(score, filename):
    mf = m21.midi.translate.streamToMidiFile(score)
    mf.open(filename, 'wb')
    mf.write()
    mf.close()


def get_degree(key, pitch):
    return key.getScaleDegreeFromPitch(pitch, comparisonAttribute='pitchClass')
