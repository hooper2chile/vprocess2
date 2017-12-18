#!/usr/bin/env python
#--*- coding: utf-8 -*--

import zmq, time

tau_zmq_connect     = 0.5


#escucha los zmq emitidos por myserial.py
port_sub = "5557"
context_sub = zmq.Context()
socket_sub = context_sub.socket(zmq.SUB)
socket_sub.connect ("tcp://localhost:%s" % port_sub)
topicfilter = "w"
socket_sub.setsockopt(zmq.SUBSCRIBE, topicfilter)
time.sleep(tau_zmq_connect)

string = ['','','','']

while True:
    string = socket_sub.recv().split()
    print "\n         pH,    oD,    Temp1,     Iph,   Iod,   Itemp1,   Itemp2"
    print string
    time.sleep(0.05)
