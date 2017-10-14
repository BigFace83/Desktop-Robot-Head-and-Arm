# |B|I|G| |F|A|C|E| |R|O|B|O|T|I|C|S|

import serial
import time

print ("Opening Serial Port")
ser = serial.Serial('/dev/ttyACM0', 115200, timeout = 10)
time.sleep(1) # wait here a bit, let arduino boot up fully before sending data
print ("Port open:  " + ser.portstr)       # check which port was really used
ser.flushInput()


def readserial():
    while True:
        if ser.inWaiting()>0:
            #time.sleep(0.1) #let all of the data get here
            line = ser.readline()
            return line.rstrip('\r\n')


def sendcommand(serialdata):
    ser.write(serialdata + '\n') #Write data string, newline terminated
    #while True: #Wait here until the returned string is received
    #    if ser.inWaiting()>0:
    #        #time.sleep(0.1) #let all of the data get here
    #        line = ser.readline()
    #        return line.rstrip('\r\n')

def closeserial():
    ser.close() 
