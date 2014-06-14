"""

Handles a baudot teletype attached to GPIO of a raspberry pi 

"""
import webiopi
import time
import binascii
import urllib # for url unquote
import threading


gpio = webiopi.GPIO
PWR_RLY          = 7 # GPIO Chan used for power
DATA_RLY         = 8 # GPIO Chan used for data
gpio8period      = 20 # period of 1 bit to achieve 45bps

MotorTimerVal         = 2 # seconds for motor to stay on after last character
MotorTimerCtr         = 0 # counts down for motor
MotorTimerThread      = None # motor timer taken care of on a separate thread
ColumnCurrentPosition = 1
ColumnMax             = 72
 
# first we map ascii to the possible ascii chars
ascii_to_baudot_char = {
  'a':'A',
  'b':'B',
  'c':'C',
  'd':'D',
  'e':'E',
  'f':'F',
  'g':'G',
  'h':'H',
  'i':'I',
  'j':'J',
  'k':'K',
  'l':'L',
  'm':'M',
  'n':'N',
  'o':'O',
  'p':'P',
  'q':'Q',
  'r':'R',
  's':'S',
  't':'T',
  'u':'U',
  'v':'V',
  'w':'W',
  'x':'X',
  'y':'Y',
  'z':'Z',
  'A':'A',
  'B':'B',
  'C':'C',
  'D':'D',
  'E':'E',
  'F':'F',
  'G':'G',
  'H':'H',
  'I':'I',
  'J':'J',
  'K':'K',
  'L':'L',
  'M':'M',
  'N':'N',
  'O':'O',
  'P':'P',
  'Q':'Q',
  'R':'R',
  'S':'S',
  'T':'T',
  'U':'U',
  'V':'V',
  'W':'W',
  'X':'X',
  'Y':'Y',
  'Z':'Z',
  '1':'1',
  '2':'2',
  '3':'3',
  '4':'4',
  '5':'5',
  '6':'6',
  '7':'7',
  '8':'8',
  '9':'9',
  '0':'0',
  '-': '-',
  '?': '?',
  ':': ':',
  '$': '$',
  '!': '!',
  '&': '&',
  '#': '#',
  '(': '(',
  ')': '(',
  '.': '.',
  ',': ',',
  '\'': '\'',
  '/': '/',
  '"': '"',
  ' ': ' ' 
}

# then we map limted set to baudot
# see http://rabbit.eng.miami.edu/info/baudot.html
ascii_to_binstr = {
  'A'  : '00011',
  'B'  : '11001',
  'C'  : '01110',
  'D'  : '01001',
  'E'  : '00001',
  'F'  : '01101',
  'G'  : '11010',
  'H'  : '10100',
  'I'  : '00110',
  'J'  : '01011',
  'K'  : '01111',
  'L'  : '10010',
  'M'  : '11100',
  'N'  : '01100',
  'O'  : '11000',
  'P'  : '10110',
  'Q'  : '10111',
  'R'  : '01010',
  'S'  : '00101',
  'T'  : '10000',
  'U'  : '00111',
  'V'  : '11110',
  'W'  : '10011',
  'X'  : '11101',
  'Y'  : '10101',
  'Z'  : '10001',
  '1'  : '10111',
  '2'  : '10011',
  '3'  : '00001',
  '4'  : '01011',
  '5'  : '10000',
  '6'  : '10101',
  '7'  : '00111',
  '8'  : '00110',
  '9'  : '11000',
  '0'  : '10110',
  '-'  : '00011',
  '?'  : '11001',
  ':'  : '01110',
  '$'  : '01001',
  '!'  : '01001',
  '&'  : '11010',
  '#'  : '10100',
  '('  : '01111',
  ')'  : '10010',
  '.'  : '11100',
  ','  : '01100',
  '\'' : '01010',
  '/'  : '11101',
  '"'  : '11101',
  ' '  : '00100'
}

needs_shift_up = (
  '1',
  '2',
  '3',
  '4',
  '5',
  '6',
  '7',
  '8',
  '9',
  '0',
  '-',
  '?',
  ':',
  '$',
  '!',
  '&',
  '#',
  '(',
  ')',
  '.',
  ',',
  '\'',
  '/',
  '"'
)


def one_sec_chores():
  """
  Called 1x as separate thread to do things like time out motor
  """
  global MotorTimerCtr, MotorTimerVal, MotorTimerThread
  #print "one_sec_chores() MotorTimerCtr: %d" % MotorTimerCtr
  if (MotorTimerCtr):
    MotorTimerCtr = MotorTimerCtr - 1
    if (not MotorTimerCtr):
      print "Motor Timer Done"
      motor_stop()

  # restart ourselves if parent thread is still alive
  for thread in threading.enumerate():
    if thread.getName().find("MainThread") != -1:
      if thread.is_alive() == True:
        MotorTimerThread = threading.Timer(1.0,one_sec_chores)
        MotorTimerThread.start()
      else:
        print "one_sec_chores(): Parent process died. Exiting."
  

def init(gpio_arg):
  """
  initialize teletype i/o
  """
  gpio = gpio_arg
  gpio.setFunction(PWR_RLY,gpio.OUT)
  gpio.setFunction(DATA_RLY,gpio.OUT)
  gpio.output(PWR_RLY,gpio.HIGH)
  gpio.output(DATA_RLY,gpio.HIGH)

  # set a 1 sec timer for motor
  one_sec_chores() # call it once to get things rolling


"""
  tx("00000") # null
  tx("00000") # null
  tx("00000") # null
  tx("01000") # cr
  time.sleep(1.0)
  tx("00010") # lf
"""


# establish timer for TTY Motor

def motor_start(time_secs=0):
  """
  turn on motor
  """
  global MotorTimerCtr, MotorTimerVal

  if (not MotorTimerCtr) :
    print "Motor start"
    gpio.output(PWR_RLY,gpio.LOW)
    time.sleep(.25)
  
  if not time_secs:
    MotorTimerCtr = MotorTimerVal
  else:
    print "motor_start(): non-standard timeout value: %d" % time_secs
    MotorTimerCtr = time_secs

def motor_stop():
  """
  turn off motor, turn off data relay
  """
  global MotorTimerCtr
  gpio.output(PWR_RLY,gpio.HIGH)
  time.sleep(2.0)
  gpio.output(DATA_RLY,gpio.HIGH)
  MotorTimerCtr = 0

def test(s):
  """
  various tests
  """
  if (s == 'allpats'):
    """
    test mapping tables by attempt to print out all possible codes
    """
    print 'allpats'
    for i in range(0,256):
      if (ascii_to_baudot_char.has_key(chr(i))): # if first reduce mapping table has key
        a = ascii_to_baudot_char[chr(i)]
        #print 'ascii_to_baudot_char(%d): %s' % (i,a)
        if (ascii_to_binstr.has_key(a)): # and 2nd reduce mapping table has key
          b = ascii_to_binstr[a]
          if (b != '00000'):
            print 'test(%s)' % (a)
            txbaudot(b)
   
def txbaudot(c):
  """
  transmit one character to the teletype
  """

  motor_start()

  gpio.outputSequence(DATA_RLY,gpio8period, "0") #start
  gpio.outputSequence(DATA_RLY,gpio8period, c[::-1]) # [::-1] reverses the order
  gpio.outputSequence(DATA_RLY,gpio8period, "1") #stop
  gpio.outputSequence(DATA_RLY,gpio8period, "1") #stop

def txbin(s):
  txbaudot(s)

def tx_keycode(s):
  print 'tx_keycode(%s)' % (s)
  k = int(s)
  if (ascii_to_baudot_char.has_key(chr(k))):
      a = ascii_to_baudot_char[chr(k)]
      #print 'ascii_to_baudot_char(%d): %s' % (i,a)
      if (ascii_to_binstr.has_key(a)): # and 2nd reduce mapping table has key
        b = ascii_to_binstr[a]
        print 'tx_keycode() %d (%s) -> (%s)' % (k,chr(k),b)
        if (b != '00000'):
          print 'tx_keycode(%s)' % (b)
          txbaudot(b)

shifted = False

def update_column_position():
  """
  keep track of column position so we can insert cr lf when necessary
  """
  global ColumnCurrentPosition, ColumnMax
  ColumnCurrentPosition = ColumnCurrentPosition + 1
  if ColumnCurrentPosition > ColumnMax:
    print "update_column_position(): col 0"
    tx_ctl('cr')
    tx_ctl('lf')
    ColumnCurrentPosition = 0; print "column reset to 0"

def shift_up():
  """
  Shift up to figures
  """
  global shifted
  if not shifted:
    tx_ctl('figs')
    shifted = True

def shift_down():
  """
  Shift down to letters
  """
  global shifted
  if shifted:
    tx_ctl('ltrs')
    shifted = False


def tx_ascii_chr(c):
  """
  send an ascii character
  """
  if (ascii_to_baudot_char.has_key(c)):
      a = ascii_to_baudot_char[c]
      #print 'ascii_to_baudot_char(%d): %s' % (i,a)
      if (ascii_to_binstr.has_key(a)): # and 2nd reduce mapping table has key
        b = ascii_to_binstr[a]
        if (b != '00000'):
          #print 'tx_ascii_chr(%s)' % (b)
          if (a in needs_shift_up):
            shift_up()
          else:
            shift_down()
          txbaudot(b)
          update_column_position()



def tx(c):
  """
  send an ascii character
  """
  tx_keycode(c)

def tx_str(s):
  """
  transmit an ascii string
  """
  de_uried_str = urllib.unquote(s)
  for i in range(len(de_uried_str)):
    print '[%s]' % de_uried_str[i]
    tx_ascii_chr(de_uried_str[i])


def tx_ctl(c):
  """
  transmit a control code 'lf' = line feed, 'cr' = carriage return, etc.
  """
  global ColumnCurrentPosition
  print "tx_ctl(%s)" % c
  if (c == 'cr'):
    txbaudot('01000')
    ColumnCurrentPosition = 0
  elif (c == 'lf'):
    txbaudot('00010')
  elif (c == 'figs'):
    txbaudot('11011')
  elif (c == 'ltrs'):
    txbaudot('11111')
  elif (c == 'bell'):
    txbaudot('11011') # shift up
    txbaudot('00101')
    txbaudot('11111') # shift down
    txbaudot('01000') # cr
    txbaudot('00100') # space
    txbaudot('00100')
    txbaudot('00100')
    txbaudot('00100')
    txbaudot('00100')
    txbaudot('00100')
    txbaudot('00100')
    txbaudot('00100')
    txbaudot('01000') # cr
    ColumnCurrentPosition = 0
  elif (c == 'null'):
    txbaudot('00000')
  elif (c == 'space'):
    txbaudot('00100')
    update_column_position()
  else:
    print 'no action'

