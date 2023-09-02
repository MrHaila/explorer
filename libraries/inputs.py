from pimoroni import Analog # type: ignore
from libraries import midi # https://github.com/sensai7/Micropython-midi-library

# A class to represent a potentiometer.
class Potentiometer:
  previous_value = 0
  previous_previous_value = 0
  previously_sent_value = 0
  channel = 1
  cc = 1

  def __init__(self, midi_instance: midi.Midi, pin: int, invert: bool = False, channel: int = 1, cc: int = 1):
    self.adc = Analog(pin)
    self.invert = invert
    self.midi_instance = midi_instance
    self.channel = channel
    self.cc = cc

  def increment_channel(self):
    if self.channel < 16:
      self.channel += 1
      return True
    else:
      return False
  
  def decrement_channel(self):
    if self.channel > 1:
      self.channel -= 1
      return True
    else:
      return False

  def increment_cc(self):
    if self.cc < 127:
      self.cc += 1
      return True
    else:
      return False

  def decrement_cc(self):
    if self.cc > 1:
      self.cc -= 1
      return True
    else:
      return False

  def set_channel(self, channel: int):
    if channel < 1:
      channel = 1
    elif channel > 16:
      channel = 16
    self.channel = channel

  def set_cc(self, cc: int):
    if cc < 1:
      cc = 1
    elif cc > 127:
      cc = 127
    self.cc = cc

  def read_voltage(self):
    return self.adc.read_voltage()
  
  def read_voltage_as_midi(self):
    value = self.adc.read_voltage()
    value = value / 3.3
    value = value * 127
    if self.invert:
      value = 127 - value
    value = int(value)

    # Prevent the value from juping back and forth between two values.
    if value == 0 or (value != self.previous_value and value != self.previous_previous_value):
      self.previous_previous_value = self.previous_value
      self.previous_value = value
      return value
    else:
      return self.previous_value
    
  def send_midi_cc_if_needed(self, value):
    if value is None:
      value = self.read_voltage_as_midi()

    if value != self.previously_sent_value:
      self.midi_instance.send_control_change(channel=self.channel, cc=self.cc, value=value)
      self.previously_sent_value = value