"""

Raspberry Pi Teletype WebIOPi Application

To run: 
  python app.py

"""

import webiopi
import time
import teletype

GPIO = webiopi.GPIO # Retrieve GPIO lib

# these are the particular GPIO Pins we used. 
PWR_RLY=7  # runs an opto-isolated relay which toggles power
DATA_RLY=8 # runs an opto-isolated N-Channel mosfet which toggles relay

# empiracally-determined delay factor for teletype's bit rate
gpio8period = 20


def baud_rate_inc():
  global gpio8period
  gpio8period = gpio8period + 1
  print repr(gpio8period)

def baud_rate_dec():
  global gpio8period
  if (gpio8period > 1):
    gpio8period = gpio8period - 1
  print repr(gpio8period)


def tty_start():
  teletype.motor_start(time_secs=30)

def tty_stop():
  teletype.motor_stop()

def tty_tx(c):
  teletype.tx(c)

def tty_tx_str(s):
  print repr(s)
  teletype.tx_str(s)

def tty_tx_ctl(c):
  teletype.tx_ctl(c)


def tty_test(s):
  teletype.test(s)


MotorOnCounter = 10

def loop():
  # Example loop which toggle GPIO 7 each 5 seconds
  #GPIO.output(PWR_RLY not GPIO.input(7))
  #                                   sdddddss
  """
  teletype.tx("00010")
  teletype.tx("00100")
  teletype.tx("01000")
  teletype.tx("10000")
  teletype.tx("11011") # shift to figures
  teletype.tx("00101") # bell
  teletype.tx("11111") # letters
  teletype.tx("00101") # bell
  teletype.tx("00100") # space
  teletype.tx("00100") # space
  teletype.tx("00100") # space
  teletype.tx("01000") # cr
  teletype.tx("11011") # shift to figures
  teletype.tx("00100") # space
  teletype.tx("00100") # space
  teletype.tx("00100") # space
  teletype.tx("00100") # space
  teletype.tx("00100") # space
  teletype.tx("11111")
  teletype.tx("00010")
  teletype.tx("00100")
  teletype.tx("01000")
  teletype.tx("10000")
  GPIO.outputSequence(DATA_RLY,gpio8period, "0101010101010101010101010101")
  GPIO.outputSequence(DATA_RLY,gpio8period, "0101010101010101010101010101")
  GPIO.outputSequence(DATA_RLY,gpio8period, "0101010101010101010101010101")
  GPIO.outputSequence(DATA_RLY,gpio8period, "0101010101010101010101010101")
  GPIO.outputSequence(DATA_RLY,gpio8period, "0101010101010101010101010101")
  GPIO.outputSequence(DATA_RLY,gpio8period, "0101010101010101010101010101")
  GPIO.outputSequence(DATA_RLY,gpio8period, "0101010101010101010101010101")
  GPIO.outputSequence(DATA_RLY,gpio8period, "0101010101010101010101010101")
  GPIO.outputSequence(DATA_RLY,gpio8period, "0101010101010101010101010101")
  """

  
if __name__ == "__main__":

  """
  execution starts here
  """

  # webiopi.setDebug() # be verbose on stderr

  teletype.init(webiopi.GPIO)

  server = webiopi.Server(port=80,coap_port=None)

  server.host="192.168.42.1"

  server.addMacro(baud_rate_inc)
  server.addMacro(baud_rate_dec)
  server.addMacro(tty_start)
  server.addMacro(tty_stop)
  server.addMacro(tty_tx)
  server.addMacro(tty_tx_str)
  server.addMacro(tty_tx_ctl)
  server.addMacro(tty_test)

  """
  for n in range(1,79):
    teletype.tx("00100") # space
  """

  webiopi.runLoop(loop) 

  server.stop() # Cleanly stop the server

  teletype.motor_stop()
