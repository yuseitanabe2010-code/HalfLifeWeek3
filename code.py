import time
import board
import digitalio
import analogio
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange

midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0],
    midi_out=usb_midi.ports[1],
    channel=0
)

KEY_PINS = [
    board.GP0,  board.GP1,  board.GP2,  board.GP3,
    board.GP4,  board.GP5,  board.GP6,  board.GP7,
    board.GP8,  board.GP9,  board.GP10, board.GP11
]

DRUM_NOTES = [
    35, 36, 38, 39,
    40, 41, 43, 42,
    46, 37, 71, 64
]

base_note = 48
drum_mode = False
MELODIC_CHANNEL = 0
DRUM_CHANNEL = 9

keys = []
for pin in KEY_PINS:
    key = digitalio.DigitalInOut(pin)
    key.direction = digitalio.Direction.INPUT
    key.pull = digitalio.Pull.UP
    keys.append(key)

btn_oct_down = digitalio.DigitalInOut(board.GP12)
btn_oct_down.direction = digitalio.Direction.INPUT
btn_oct_down.pull = digitalio.Pull.UP

btn_oct_up = digitalio.DigitalInOut(board.GP13)
btn_oct_up.direction = digitalio.Direction.INPUT
btn_oct_up.pull = digitalio.Pull.UP

sw_drum = digitalio.DigitalInOut(board.GP14)
sw_drum.direction = digitalio.Direction.INPUT
sw_drum.pull = digitalio.Pull.UP


slide_pot = analogio.AnalogIn(board.GP26)


key_states = [False] * len(keys)
last_oct_down = False
last_oct_up = False
last_drum_sw = False
last_cc_val = -1

while True:
    is_drum_sw = not sw_drum.value
    if is_drum_sw != last_drum_sw:
        drum_mode = is_drum_sw
        midi.channel = DRUM_CHANNEL if drum_mode else MELODIC_CHANNEL
        print("Drum Mode Active" if drum_mode else "Melodic Mode Active")
        last_drum_sw = is_drum_sw

    is_oct_down = not btn_oct_down.value
    if is_oct_down and not last_oct_down:
        if base_note > 24:
            base_note -= 12
            print(f"Octave Down: Base Note = {base_note}")
    last_oct_down = is_oct_down

    is_oct_up = not btn_oct_up.value
    if is_oct_up and not last_oct_up:
        if base_note < 84:
            base_note += 12
            print(f"Octave Up: Base Note = {base_note}")
    last_oct_up = is_oct_up

    for i, key in enumerate(keys):
        is_pressed = not key.value
        if is_pressed != key_states[i]:
            note = DRUM_NOTES[i] if drum_mode else (base_note + i)
            if is_pressed:
                midi.send(NoteOn(note, 127))
            else:
                midi.send(NoteOff(note, 0))
            key_states[i] = is_pressed

    raw_val = slide_pot.value
    cc_val = int(raw_val / 65535 * 127)
    if abs(cc_val - last_cc_val) > 1:
        midi.send(ControlChange(7, cc_val))
        last_cc_val = cc_val

    time.sleep(0.01)
