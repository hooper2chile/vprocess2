#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, request, Response, send_from_directory, make_response
from flask_socketio import SocketIO, emit, disconnect

import os, sys, logging, communication, reviewDB, tocsv

logging.basicConfig(filename='/home/pi/vprocess2/log/app.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

DIR="/home/pi/vprocess2/"
SPEED_MAX = 100 #150 [rpm]
TEMP_MAX  = 130 #130 [ºC]
TIME_MAX  = 360 #360 [min] = 6 [HR]

u_set_temp = [SPEED_MAX,0]
u_set_ph   = [SPEED_MAX,SPEED_MAX]

time_save = 0
temp_save = 0
ac_sets = [0,0,False,False]  #ac_sets = auto clave setpoints

ph_set = [0,0,0,0]
od_set = [0,0,0,0]
temp_set = [0,0,0,0]

task = ["grabar", False]
flag_database = False

set_data = [0,0,0,0,0,1,1,1,1,1,0,0,0]
measures = [0,0,0,0,0,0,0]



# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

#app = Flask(__name__)
app = Flask(__name__, static_url_path="")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread1 = None
thread2 = None
error   = None

#CONFIGURACION DE PAGINAS WEB
@app.route('/'     , methods=['POST', 'GET'])
@app.route('/login', methods=['POST', 'GET'])
def login():
    global error

    if request.method == 'POST':
        if request.form['username'] != 'administrador' or request.form['password'] != 'gr4noteC':
            error = "Credencial Invalida"
            return render_template("login.html", error=error)
        else:
            error='validado'
            return render_template("proceso.html", error=error)

    error="No Validado en login"
    return render_template("login.html", error=error)




@app.route('/calibrar', methods=['POST', 'GET'])
def test():
    global error
    if request.method == 'POST':
        if request.form['username'] != 'administrador' or request.form['password'] != 'gr4noteC':
            error = "Credencial Invalida"
            return render_template("login.html", error=error)
        else:
            error='validado'
            return render_template("calibrar.html", error=error)


    error = 'No Validado en Calibracion'
    return render_template("login.html", error=error)


@app.route('/graphics')
def graphics():
    return render_template('graphics.html', title_html="Variables de Proceso")


@app.route('/dbase', methods=['GET', 'POST'])
def viewDB():
    return render_template('dbase.html', title_html="Data Logger")


@app.route('/autoclave', methods=['GET', 'POST'])
def autoclave():
    return render_template('autoclave.html', title_html="AutoClave")



#CONFIGURACION DE FUNCIONES SocketIO
#Connect to the Socket.IO server. (Este socket es OBLIGACION)
@socketio.on('connect', namespace='/biocl')
def function_thread():
    #print "\n Cliente Conectado al Thread del Bioreactor\n"
    logging.info("\n Cliente Conectado al Thread del Bioreactor\n")

    #Se emite durante la primera conexión de un cliente el estado actual de los setpoints
    emit('Setpoints',       {'set': set_data})
    emit('ph_calibrar',     {'set': ph_set})
    emit('od_calibrar',     {'set': od_set})
    emit('temp_calibrar',   {'set': temp_set})
    emit('u_calibrar',      {'set': u_set_ph})
    emit('u_calibrar_temp', {'set': u_set_temp})
    emit('power',           {'set': task})
    emit('ac_setpoints',    {'set': ac_sets, 'save': [temp_save, time_save]})


    global thread1
    if thread1 is None:
        thread1 = socketio.start_background_task(target=background_thread1)



@socketio.on('power', namespace='/biocl')
def system(dato):
    global task, flag_database
    #se reciben las nuevos acciones: apagar, reiniciar, borrar archivos, etc
    task = [ dato['action'], dato['checked'] ]

    #guardo task en un archivo para depurar
    try:
        f = open(DIR + "task.txt","a+")
        f.write(task + '\n')
        f.close()

    except:
        pass
        #logging.info("no se pudo guardar en realizar en task.txt")


    #Con cada cambio en los setpoints, se vuelven a emitir a todos los clientes.
    socketio.emit('power', {'set': task}, namespace='/biocl', broadcast=True)

    if task[1] is True:
        if task[0] == "grabar":
            flag_database = "True"
            try:
                f = open(DIR + "flag_database.txt","w")
                f.write(flag_database)
                f.close()

            except:
                pass
                #logging.info("no se pudo guardar el flag_database para iniciar grabacion\n")

        elif task[0] == "no_grabar":
            flag_database = "False"
            try:
                f = open(DIR + "flag_database.txt","w")
                f.write(flag_database)
                f.close()

            except:
                pass
                #logging.info("no se pudo guardar el flag_database para detener grabacion\n")

        elif task[0] == "reiniciar":
            os.system(DIR + "bash killall")
            os.system("sudo reboot")

        elif task[0] == "apagar":
            os.system(DIR + "bash killall")
            os.system("sudo shutdown -h now")

        elif task[0] == "limpiar":
            try:
                os.system("rm -rf /home/pi/vprocess2/csv/*.csv")
                os.system("rm -rf /home/pi/vprocess2/log/*.log")
                os.system("rm -rf /home/pi/vprocess2/log/my.log.*")
                os.system("rm -rf /home/pi/vprocess2/database/*.db")
                os.system("rm -rf /home/pi/vprocess2/database/*.db-journal")

            except:
                pass
                #logging.info("no se pudo completar limpiar\n")





N = None
APIRest = None
@socketio.on('my_json', namespace='/biocl')
def my_json(dato):

    dt  = int(dato['dt'])
    var = dato['var']

    try:
        f = open(DIR + "window.txt","a+")
        f.write(dato['var'] + ' ' + dato['dt'] +'\n')
        f.close()

    except:
        pass
        #print "no se logro escribir la ventana solicitada en el archivo window.txt"
        #logging.info("no se logro escribir la ventana solicitada en el archivo window.txt")

    #Se buscan los datos de la consulta en database
    try:
        f = open(DIR + "name_db.txt",'r')
        filedb = f.readlines()[-1][:-1]
        f.close()

    except:
        pass
        #print "no se logro leer nombre de ultimo archivo en name_db.txt"
        #logging.info("no se logro leer nombre de ultimo archivo en name_db.txt")

    global APIRest
    APIRest = reviewDB.window_db(filedb, var, dt)
    socketio.emit('my_json', {'data': APIRest, 'No': len(APIRest), 'var': var}, namespace='/biocl')
    #put files in csv with dt time for samples
    tocsv.csv_file(filedb, dt)




@socketio.on('Setpoints', namespace='/biocl')
def setpoints(dato):
    global set_data
    #se reciben los nuevos setpoints
    set_data = [ dato['alimentar'], dato['mezclar'], dato['ph'], dato['descarga'], dato['temperatura'], dato['alimentar_rst'], dato['mezclar_rst'], dato['ph_rst'], dato['descarga_rst'], dato['temperatura_rst'], dato['alimentar_dir'], dato['ph_dir'], dato['temperatura_dir'] ]

    #Con cada cambio en los setpoints, se vuelven a emitir a todos los clientes.
    socketio.emit('Setpoints', {'set': set_data}, namespace='/biocl', broadcast=True)

    #guardo set_data en un archivo para depurar
    try:
        settings = str(set_data)
        f = open(DIR + "setpoints.txt","a+")
        f.write(settings + '\n')
        f.close()

    except:
        pass
        #logging.info("no se pudo guardar en set_data en setpoints.txt")


#Sockets de calibración de instrumentación
#CALIBRACION DE PH
@socketio.on('ph_calibrar', namespace='/biocl')
def calibrar_ph(dato):
    global ph_set
    #se reciben los parametros para calibración
    setting = [ dato['ph'], dato['iph'], dato['medx'] ]

    #ORDEN DE: ph_set:
    #ph_set = [ph1_set, iph1_set, ph2_set, iph2_set]
    try:
        if setting[2] == 'med1':
            ph_set[0] = float(dato['ph'])   #y1
            ph_set[1] = float(dato['iph'])  #x1

        elif setting[2] == 'med2':
            ph_set[2] = float(dato['ph'])   #y2
            ph_set[3] = float(dato['iph'])  #x2

    except:
        ph_set = [0,0,0,0]

    if (ph_set[3] - ph_set[1])!=0 and ph_set[0]!=0 and ph_set[1]!=0:
        m_ph = float(format(( ph_set[2] - ph_set[0] )/( ph_set[3] - ph_set[1] ), '.2f'))
        n_ph = float(format(  ph_set[0] - ph_set[1]*(m_ph), '.2f'))

    else:
        m_ph = 0
        n_ph = 0

    if ph_set[0]!=0 and ph_set[1]!=0 and ph_set[2]!=0 and ph_set[3]!=0 and m_ph!=0 and n_ph!=0:
        try:
            coef_ph_set = [m_ph, n_ph]
            f = open(DIR + "coef_ph_set.txt","w")
            f.write(str(coef_ph_set) + '\n')
            f.close()
            #acá va el codigo que formatea el comando de calibración.
            communication.calibrate(0,coef_ph_set)

        except:
            pass
            #logging.info("no se pudo guardar en coef_ph_set.txt. Tampoco actualizar los coef_ph_set al uc.")

    #Con cada cambio en los parametros, se vuelven a emitir a todos los clientes.
    socketio.emit('ph_calibrar', {'set': ph_set}, namespace='/biocl', broadcast=True)

    #guardo set_data en un archivo para depurar
    try:
        ph_set_txt = str(ph_set)
        f = open(DIR + "ph_set.txt","w")
        f.write(ph_set_txt + '\n')
        f.close()

    except:
        pass
        #logging.info("no se pudo guardar parameters en ph_set.txt")



#CALIBRACION OXIGENO DISUELTO
@socketio.on('od_calibrar', namespace='/biocl')
def calibrar_od(dato):
    global od_set
    #se reciben los parametros para calibración
    setting = [ dato['od'], dato['iod'], dato['medx'] ]

    #ORDEN DE: od_set:
    #ph_set = [od1_set, iod1_set, od2_set, iod2_set]
    try:
        if setting[2] == 'med1':
            od_set[0] = float(dato['od'])
            od_set[1] = float(dato['iod'])

        elif setting[2] == 'med2':
            od_set[2] = float(dato['od'])
            od_set[3] = float(dato['iod'])

    except:
        od_set = [0,0,0,0]


    if (od_set[3] - od_set[1])!=0 and od_set[1]!=0:
        m_od = float(format(( od_set[2] - od_set[0] )/( od_set[3] - od_set[1] ), '.2f'))
        n_od = float(format(  od_set[0] - od_set[1]*(m_od), '.2f'))

    else:
        m_od = 0
        n_od = 0

    if od_set[1]!=0 and od_set[3]!=0 and m_od!=0 and n_od!=0:
        try:
            coef_od_set = [m_od, n_od]
            f = open(DIR + "coef_od_set.txt","w")
            f.write(str(coef_od_set) + '\n')
            f.close()

            communication.calibrate(1,coef_od_set)


        except:
            pass
            #logging.info("no se pudo guardar en coef_ph_set en coef_od_set.txt")


    #Con cada cambio en los parametros, se vuelven a emitir a todos los clientes.
    socketio.emit('od_calibrar', {'set': od_set}, namespace='/biocl', broadcast=True)

    #guardo set_data en un archivo para depurar
    try:
        od_set_txt = str(od_set)
        f = open(DIR + "od_set.txt","w")
        f.write(od_set_txt + '\n')
        f.close()

    except:
        pass
        #logging.info("no se pudo guardar parameters en od_set.txt")


#CALIBRACIÓN TEMPERATURA
@socketio.on('temp_calibrar', namespace='/biocl')
def calibrar_temp(dato):
    global temp_set
    #se reciben los parametros para calibración
    setting = [ dato['temp'], dato['itemp'], dato['medx'] ]

    #ORDEN DE: od_set:
    #ph_set = [od1_set, iod1_set, od2_set, iod2_set]
    try:
        if setting[2] == 'med1':
            temp_set[0] = float(dato['temp'])
            temp_set[1] = float(dato['itemp'])

        elif setting[2] == 'med2':
            temp_set[2] = float(dato['temp'])
            temp_set[3] = float(dato['itemp'])

    except:
        temp_set = [0,0,0,0]

    if (temp_set[3] - temp_set[1])!=0 and temp_set[0]!=0 and temp_set[1]!=0:
        m_temp = float(format(( temp_set[2] - temp_set[0] )/( temp_set[3] - temp_set[1] ), '.2f'))
        n_temp = float(format(  temp_set[0] - temp_set[1]*(m_temp), '.2f'))

    else:
        m_temp = 0
        n_temp = 0

    if temp_set[0]!=0 and temp_set[1]!=0 and temp_set[2]!=0 and temp_set[3]!=0 and m_temp!=0 and n_temp!=0:
        try:
            coef_temp_set = [m_temp, n_temp]
            f = open(DIR + "coef_temp_set.txt","w")
            f.write(str(coef_temp_set) + '\n')
            f.close()

            communication.calibrate(2,coef_temp_set)


        except:
            pass
            #logging.info("no se pudo guardar en coef_ph_set en coef_od_set.txt")


    #Con cada cambio en los parametros, se vuelven a emitir a todos los clientes.
    socketio.emit('temp_calibrar', {'set': temp_set}, namespace='/biocl', broadcast=True)

    #guardo set_data en un archivo para depurar
    try:
        temp_set_txt = str(temp_set)
        f = open(DIR + "temp_set.txt","w")
        f.write(temp_set_txt + '\n')
        f.close()

    except:
        pass
        #logging.info("no se pudo guardar parameters en temp_set.txt")



#CALIBRACION ACTUADOR PH
@socketio.on('u_calibrar', namespace='/biocl')
def calibrar_u_ph(dato):
    global u_set_ph
    #se reciben los parametros para calibración
    #setting = [ dato['u_acido_max'], dato['u_base_max'] ]

    try:
        u_set_ph[0] = int(dato['u_acido_max'])
        u_set_ph[1] = int(dato['u_base_max'])

    except:
        u_set_ph = [SPEED_MAX,SPEED_MAX]


    try:
        f = open(DIR + "umbral_set_ph.txt","w")
        f.write(str(u_set_ph) + '\n')
        f.close()
        communication.actuador(1,u_set_ph)  #FALTA IMPLEMENTARIO EN communication.py

    except:
        pass
        #logging.info("no se pudo guardar umbrales u_set_ph en umbral_set_ph.txt")


    #Con cada cambio en los parametros, se vuelven a emitir a todos los clientes.
    socketio.emit('u_calibrar', {'set': u_set_ph}, namespace='/biocl', broadcast=True)



#CALIBRACION ACTUADOR TEMP
@socketio.on('u_calibrar_temp', namespace='/biocl')
def calibrar_u_temp(dato):
    global u_set_temp
    #se reciben los parametros para calibración

    try:
        u_set_temp[0] = int(dato['u_temp'])
        u_set_temp[1] = 0

    except:
        u_set_temp = [SPEED_MAX,SPEED_MAX]


    try:
        f = open(DIR + "umbral_set_temp.txt","w")
        f.write(str(u_set_temp) + '\n')
        f.close()
        communication.actuador(2,u_set_temp)  #FALTA IMPLEMENTARIO EN communication.py

    except:
        pass
        #logging.info("no se pudo guardar u_set_temp en umbral_set_temp.txt")


    #Con cada cambio en los parametros, se vuelven a emitir a todos los clientes.
    socketio.emit('u_calibrar_temp', {'set': u_set_temp}, namespace='/biocl', broadcast=True)



@socketio.on('ac_setpoints', namespace='/biocl')
def autoclave_functions(dato):
    global ac_sets, time_save, temp_save

    try:
        ac_sets[0] = int(dato['ac_temp'])
        ac_sets[1] = int(dato['ac_time'])
        ac_sets[2] = dato['time_en']
        ac_sets[3] = dato['temp_en']

        temp_save = int(dato['ac_temp'])
        time_save = int(dato['ac_time'])

    except:
        ac_sets[0] = 22
        ac_sets[1] = 11
    	ac_sets[2] = "no_llego"
    	ac_sets[3] = "no_llego"

        time_save = "vacio"
        temp_save = "vacio"

    if ac_sets[0] > TEMP_MAX:
        ac_sets[0] = TEMP_MAX

    if ac_sets[1] > TIME_MAX:
        ac_sets[1] = TIME_MAX


    #Con cada cambio en los parametros, se vuelven a emitir a todos los clientes.
    socketio.emit('ac_setpoints', {'set': ac_sets, 'save': [temp_save, time_save]}, namespace='/biocl', broadcast=True)


    #función TimeCounter: poner acá, posiblemente con thread2, falta recibir la confirmación de activación
    global thread2
    if thread2 is None:
        thread2 = socketio.start_background_task(target=background_thread2)


    try:
        f = open(DIR + "autoclave.txt","a+")
     	f.write(str(ac_sets) + ', ' + str(time_save) + ', ' + str(temp_save) + '\n')
    	f.close()
	#logging.info("se guardo en autoclave.txt")

    except:
        pass
	#logging.info("no se pudo guardar en autoclave.txt")


#ac_sets[0] =: temperatura de autoclavado
#ac_sets[1] =: tiempo de autoclavado
#ac_sets[2] =: flag deshabilitar control temperatura webpage proceso
#ac_sets[3] =: flag habilitar (AutoClave) webpage esterilizacion
#CONFIGURACION DE THREADS
def background_thread2():
    global ac_sets, time_save, temp_save, thread2, measures
    while True:
        communication.cook_autoclave('d')  # partimos poniendo bomba y valvulas a default (OFF)
        while ac_sets[1] > 0: # "mientras el tiempo continua corriendo"
            if float(measures[2]) >= temp_save:   # "si la temperatura es mayor que la temperatura seteada"
                communication.cook_autoclave('o') # entonces no seguir calentando, ni enfriar, 'n' es solamente recircular
                socketio.sleep(60) # 60[s]
                ac_sets[1] -= 1   # ac_sets[1]=: timer set, ac_sets[2]=: temperatura set???
                socketio.emit('ac_setpoints', {'set': ac_sets, 'save': [temp_save, time_save]}, namespace='/biocl', broadcast=True)

            else:
                ac_sets[1] = time_save    # repone el tiempo seteado en caso que rompa la "cadena de calor de autoclavado" para reiniciarlo
                socketio.emit('ac_setpoints', {'set': ac_sets, 'save': [temp_save, time_save]}, namespace='/biocl', broadcast=True)
                communication.cook_autoclave('v') # sino aplicar vapor al intercambiador
                socketio.sleep(0.5) #para no matar el procesador cuando no pasa nada...

        if ac_sets[1] <= 0:
                ac_sets[1] = 0  #asegurando el valor

        communication.cook_autoclave('d')  # terminamos poniendo bomba y valvulas a default (OFF)
        socketio.sleep(0.5) #para no matar el procesador cuando no pasa nada..




def background_thread1():
    save_set_data = [0,0,0,0,0,1,1,1,1,1,0,0,0]
    k = 0

    global set_data, measures
    while True:
        #se emiten las mediciones y setpoints para medir y graficar
        socketio.emit('Medidas', {'data': measures, 'set': set_data}, namespace='/biocl')

        #ZMQ DAQmx download data from micro controller: app.py<->communication.py<->myserial.py<->uc
        temp_ = communication.zmq_client().split()

        try:
            measures[0] = temp_[1]  #ph
            measures[1] = temp_[2]  #oD
            measures[2] = temp_[3]  #Temp1
            measures[3] = temp_[4]  #Iph
            measures[4] = temp_[5]  #Iod
            measures[5] = temp_[6]  #Itemp1
            measures[6] = temp_[7]  #Itemp2


            for i in range(0,len(set_data)):
                if save_set_data[i] != set_data[i]:
                    communication.cook_setpoint(set_data)
                    save_set_data = set_data

            #### TEST ######
            '''
            if k == 8:
                k = 0
                communication.cook_setpoint(save_set_data)
                f = open(DIR + "motor_resend.txt","a+")
             	f.write(str(set_data) + '\n')
            	f.close()

            else:
                k += 1
            '''
            #################

            #logging.info("\n Se ejecuto Thread 1 emitiendo %s\n" % set_data)

        except:
            pass
            #logging.info("\n no se actualizaron las mediciones")

        socketio.sleep(0.25)





if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
