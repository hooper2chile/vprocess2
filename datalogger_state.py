import os, time



DIR = "/home/pi/vprocess/"

while True:
    f = open(DIR + "datalogger_state.txt", 'a')
    now = time.strftime("%H:%M:%S")
    f.write("son las: " + now)
    f.close()
    time.sleep(5)
