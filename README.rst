pyrttl
=======

Pyrttl is a library for processing of
RTTL (Ring Tone Transfer Language, http://en.wikipedia.org/wiki/Ring_Tone_Transfer_Language) files.
You can use it to parse and process (e.g. convert to MIDI) ringtone tunes in RTTL format.

Installation
------------

To install using `pip`::

	pip install -e git+https://github.com/mwicat/pyrttl.git#egg=pyrttl

Scripts
---------------

To convert RTTL file to MIDI:

    rttlproc midi -i Offspring\ -\ The\ Kids\ Aren\'t\ Alright.txt -o offspring.mid

To dump RTTL information:

    rttlproc dump -i Offspring\ -\ The\ Kids\ Aren\'t\ Alright.txt
