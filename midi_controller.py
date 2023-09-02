from picographics import PicoGraphics, DISPLAY_PICO_EXPLORER # type: ignore
from machine import Pin
from pimoroni import Button, Buzzer # type: ignore
import time
import _thread

from libraries import midi, inputs # https://github.com/sensai7/Micropython-midi-library

display = PicoGraphics(display=DISPLAY_PICO_EXPLORER)
WIDTH, HEIGHT = display.get_bounds()
display.set_backlight(0)

# Create a MIDI instance.
MIDI_TX_PIN = Pin(8)
MIDI_RX_PIN = Pin(9)
midi_instance = midi.Midi(1, tx=MIDI_TX_PIN, rx=MIDI_RX_PIN)

# Initialise inputs.
potentiometer = inputs.Potentiometer(pin=26, invert=True, midi_instance=midi_instance)
button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

# Initialise buzzer.
buzzer = Buzzer(0)

lock = _thread.allocate_lock()
def buzzer_thread(frequency: int):
  global lock
  lock.acquire()
  buzzer.set_tone(frequency)
  time.sleep(0.01)
  buzzer.set_tone(0)
  lock.release()

def try_buzz(frequency: int = 1000):
  if lock.locked():
    return
  _thread.start_new_thread(buzzer_thread, (frequency,))

while True:
  # Clear the screen.
  display.set_pen(display.create_pen(0, 0, 0))
  display.clear()

  if button_a.read():
    if potentiometer.increment_channel():
      try_buzz()

  if button_b.read():
    if potentiometer.decrement_channel():
      try_buzz(900)

  if button_x.read():
    if potentiometer.increment_cc():
      try_buzz()

  if button_y.read():
    if potentiometer.decrement_cc():
      try_buzz(900)
  
  # Read the voltage from the potentiometer and map it to a value between 0 and 1.
  value = potentiometer.read_voltage_as_midi()
  potentiometer.send_midi_cc_if_needed(value=value)

  display.set_pen(display.create_pen(255, 255, 255))

  # Draw the potentiometer value.
  display.text("Potentiometer", 2, 2, scale=2)
  display.text("Channel %s CC %s: %s"%(potentiometer.channel, potentiometer.cc, value), 2, 20, scale=2)

  # Draw date.
  display.text("2023-09-02", 2, HEIGHT - 8, scale=1)

  # Update the display.
  display.update()