import os, pty, serial, time, io

master, slave = pty.openpty()
s_name = os.ttyname(slave)

ser = serial.Serial(s_name,9600)
print(ser.is_open)
print(ser.name)
counter = 0
for i in range(10):
    ser.write(str.encode("Write counter: %d \n"%(counter)))
    print(str.encode("Write counter: %d \n"%(counter)))
    time.sleep(1)
    counter += 1

while(1):
    x=ser.read()
    print (x)

ser.close()
