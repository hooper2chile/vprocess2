import os, time



DIR = "/home/pi/vprocess2/"

while True:
    f = open(DIR + "datalogger_state.txt", 'a')
    now = time.strftime("%H:%M:%S")
    f.write("Estoy encendido a las: " + now + '\n')
    f.close()
    time.sleep(60)
