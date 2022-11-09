# Importing Libraries
import serial
import time

class arduinoComm():
    def __init__(self):
        self.arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600)
        self.commStart = self.arduino.is_open
        print("Arduino port is open? " ,self.commStart)
# def write_read(x):
#     arduino.write(bytes(x, 'utf-8'))
#     time.sleep(0.05)
#     data = arduino.readline()
#     return data
        # print(arduino.is_open)
    def readCanLine(self):
                
        # while True:
        # num = input("Enter a number: ") # Taking input from user
        value = self.arduino.readline()
        decodedValue = value.decode('utf-8')
        # print(decodedValue) # printing the value
        return decodedValue