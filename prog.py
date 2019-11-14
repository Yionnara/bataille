#!/usr/bin/python3

import socket
import select
import sys
import os
from main import *
from game import *

if len(sys.argv) == 1:
    print("Lancement du mode Serveur")
    runServerMode()
else:
    runClientMode(sys.argv[1])

def runServerMode():
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 7777))
    s.listen(1)
    clients = [s]
    while True:
        read1, write1, error1 = select.select(clients, [], [])
        for sk in read1:
            if sk == s:  #Connection
                s2, addr = s.accept()
                clients.append(s2)
                print("Connection of the address " + addr[0])
            else:  #Commands reception
                r = sk.recv(1500)
                print(r)
                line = r.decode("utf-8")
                mots = line.split()

                if r == b'':
                    print("Disonnection of the address " + sk.getsockname()[0])
                    sk.close()
                    clients.remove(sk)

def runClientMode(ServerAdress):
    os.system("nc " + ServerAdress + " 7777")
