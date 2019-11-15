#!/usr/bin/python3
from game import *
import random
import time
import sys, os
import socket, pickle
import select
import time

s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
clients = None

""" generate a random valid configuration """
def randomConfiguration():
    boats = [];
    while not isValidConfiguration(boats):
        boats=[]
        for i in range(5):
            x = random.randint(1,10)
            y = random.randint(1,10)
            isHorizontal = random.randint(0,1) == 0
            boats = boats + [Boat(x,y,LENGTHS_REQUIRED[i],isHorizontal)]
    return boats

def displayGameOver(sJ0, sJ1, game):
    print("Game over !")
    #Envoi currentPlayer de fin de partie
    sJ0.send("-1".encode("utf-8"))
    sJ1.send("-1".encode("utf-8"))
    time.sleep(0.5)
    #Envoi de sa grille
    sJ0.send(displayConfiguration(game.boats[0], game.shots[1], showBoats=True).encode("utf-8"))
    sJ1.send(displayConfiguration(game.boats[1], game.shots[0], showBoats=True).encode("utf-8"))
    time.sleep(0.5)
    #Envoi de la grille son adversaire
    sJ0.send(displayConfiguration(game.boats[1], game.shots[0], showBoats=True).encode("utf-8"))
    sJ1.send(displayConfiguration(game.boats[0], game.shots[1], showBoats=True).encode("utf-8"))
    time.sleep(0.5)
    #Envoi du gagnant
    winner = str(gameOver(game)).replace(' ', '')
    print("gameOver : ", winner)
    sJ0.send(winner.encode("utf-8"))
    sJ1.send(winner.encode("utf-8"))
    time.sleep(0.5)
    s.close()



def main():
    s = None
    clients = None
    game = None
    sJ0 = None
    sJ1 = None
    game = Game(randomConfiguration(), randomConfiguration())
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 7777))
    s.listen(1)
    clients = [s]
    waitingPlayers = True
    colDemandee = False
    ligneDemandee = False
    inGame=True
    print("En attente de clients...")
    while inGame:
        read1, write1, error1 = select.select(clients, [], [])
        for sk in read1:
            if sk == s:  #Connection
                s2, addr = s.accept()
                clients.append(s2)
                print("Connection of the address " + addr[0])
                if len(clients) > 2:
                    #Deux joueurs sont connectés : début de la partie
                    waitingPlayers = False
                    time.sleep(1)
                    print("2 players connected : Let the game begins !")
                    sJ0 = clients[1]
                    sJ1 = s2
                    #Envoyer num joueur à chaque joueur
                    sJ0.send("0".encode("utf-8"))
                    sJ1.send("1".encode("utf-8"))
                    #Envoyer le currentPlayer à chaque joueur
                    sJ0.send("0".encode("utf-8"))
                    sJ1.send("0".encode("utf-8"))
                    #Envoyer les tableaux de dispositions

                    sJ0.send(pickle.dumps((game.boats[0], game.shots[0], game.shots[1])))
                    sJ1.send(pickle.dumps((game.boats[1], game.shots[1], game.shots[0])))

                    currentPlayer = 0
            else:  #Commands reception
                r = sk.recv(1500)
                print(r)
                line = r.decode("utf-8")
                mots = line.split()
                rep = r.decode("utf-8").replace('\n','')
                if r == b'':
                    print("Disconnection of the address " + sk.getsockname()[0])
                    sk.close()
                    clients.remove(sk)

                x = ord(rep[0].capitalize())-ord("A")+1
                y = int(rep[1])
                addShot(game, x, y, currentPlayer)

                if gameOver(game) != -1:
                    displayGameOver(sJ0, sJ1, game)
                    inGame=False
                    time.sleep(1)
                    

                if currentPlayer == J0 and sk == sJ0:
                    sJ0.send("1".encode("utf-8"))
                    sJ1.send("1".encode("utf-8"))
                elif currentPlayer == J1 and sk == sJ1:
                    sJ0.send("0".encode("utf-8"))
                    sJ1.send("0".encode("utf-8"))
                else:
                    print("WRONG")
                    sys.exit(1)

                time.sleep(1)

                if inGame:
                    sJ0.send(pickle.dumps((game.boats[0], game.shots[0], game.shots[1])))
                    sJ1.send(pickle.dumps((game.boats[1], game.shots[1], game.shots[0])))
                    currentPlayer = (currentPlayer+1)%2

print("Lancement du Server...")
while True:
    print("---------NOUVELLE PARTIE-------")
    main()