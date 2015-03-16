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
octave = oneOf('4 5 6 7')
special_duration = '.'

DEFAULT_OCTAVE = 6
DEFAULT_DURATION = 4
DEFAULT_BPM = 63


def parse_tone(tone):
    note_dict = {}
    note_dict['rest'] = (tone['pitch'].lower() == 'p')

    try:
        note_dict['octave'] = int(tone['octave'])
    except (KeyError, ValueError):
        note_dict['octave'] = None

    note_dict['duration'] = tone.get('duration', None)
    note_dict['pitch'] = tone.get('pitch') if not note_dict['rest'] else None
    return note_dict


note = (
    Optional(duration).setResultsName('duration') +
    pitch.setResultsName('pitch') +
    Each([
        Optional(octave).setResultsName('octave') + Optional(special_duration).setResultsName('special-duration') +
        Optional(special_duration).setResultsName('special-duration') + Optional(octave).setResultsName('octave')]) +
    Suppress(Optional(','))
)
note.setParseAction(parse_tone)

tone_commands = Group(OneOrMore(note))

rtx = name + Suppress(':') + control_section + Suppress(':') + tone_commands + StringEnd()


def parse_rttl(s):
    s = s.strip().replace('_', '#')
    title, control_section, tone_commands = rtx.parseString(s)
    rttl_dict = {'title': title,
                 'control_section': control_section,
                 'tone_commands': tone_commands}
    return rttl_dict


def rttl2dict(rttl_data):
    rttl_dict = parse_rttl(rttl_data)
    title = rttl_dict['title']

    control_section = rttl_dict['control_section']
    tempo = control_section.get('b', DEFAULT_BPM)

    notes = rttl_dict['tone_commands']

    for note in notes:
        if note['octave'] is None:
            note['octave'] = control_section.get('o', DEFAULT_OCTAVE)
        if note['duration'] is None:
            note['duration'] = control_section.get('d', DEFAULT_DURATION)

    result = {'title': title,
              'tempo': tempo,
              'notes': list(notes)}

    return result


def rttl2score(rttl_data, analyze_key=True):
    rttl_dict = rttl2dict(rttl_data)

    title = rttl_dict['title']

    score = m21.stream.Score()
    score.metadata = m21.metadata.Metadata(title=title, composer='')

    tm = m21.tempo.MetronomeMark(number=rttl_dict['tempo'])
    score.append(tm)

    part = m21.stream.Part()
    score.append(part)

    def parse_rttl_note(note):
        quarter_length = 4. / note['duration']
        if not note['rest']:
            pitch = '%s%d' % (note['pitch'], note['octave']-1)
            return m21.note.Note(pitch, quarterLength=quarter_length)
        else:
            return m21.note.Rest(quarterLength=quarter_length)

    part.append([
        parse_rttl_note(n) for n in rttl_dict['notes']])

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
