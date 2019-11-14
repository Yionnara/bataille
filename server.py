#!/usr/bin/python3
from game import *
import random
import time
import sys, os
import socket, pickle
import select
import time

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

    sJ0.send("\n ||| GAME OVER |||\n".encode("utf-8"))
    sJ0.send("your grid : \n".encode("utf-8"))
    sJ0.send(displayConfiguration(game.boats[0], game.shots[1], showBoats=True).encode("utf-8"))
    sJ0.send("the other grid : \n".encode("utf-8"))
    sJ0.send(displayConfiguration(game.boats[1], game.shots[0], showBoats=True).encode("utf-8"))

    sJ1.send("\n ||| GAME OVER |||\n".encode("utf-8"))
    sJ1.send("your grid : \n".encode("utf-8"))
    sJ1.send(displayConfiguration(game.boats[1], game.shots[0], showBoats=True).encode("utf-8"))
    sJ1.send("the other grid : \n".encode("utf-8"))
    sJ1.send(displayConfiguration(game.boats[0], game.shots[1], showBoats=True).encode("utf-8"))

    if gameOver(game) == J0:
        sJ0.send("You won !\n".encode("utf-8"))
        sJ1.send("you lost !\n".encode("utf-8"))
    else:
        sJ0.send("you lost !\n".encode("utf-8"))
        sJ1.send("You won !\n".encode("utf-8"))



def main():
    print("Lancement du Server...")
    boats1 = randomConfiguration()
    boats2 = randomConfiguration()
    game = Game(boats1, boats2)
    #displayGame(game, 0)

    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 7777))
    s.listen(1)
    clients = [s]
    waitingPlayers = True
    sJ0 = None
    sJ1 = None
    colDemandee = False
    ligneDemandee = False
    while True:
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

                    time.sleep(1)
                    #Envoyer num joueur à chaque joueur
                    sJ0.send("0".encode("utf-8"))
                    sJ1.send("1".encode("utf-8"))

                    time.sleep(1)
                    #Envoyer le currentPlayer à chaque joueur
                    sJ0.send("0".encode("utf-8"))
                    sJ1.send("0".encode("utf-8"))

                    time.sleep(1)
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
                    
                sJ0.send(pickle.dumps((game.boats[0], game.shots[0], game.shots[1])))
                sJ1.send(pickle.dumps((game.boats[1], game.shots[1], game.shots[0])))
                # sJ0.send(displayGame(game, 0).encode("utf-8"))
                # sJ1.send(displayGame(game, 1).encode("utf-8"))
                currentPlayer = (currentPlayer+1)%2
main()