#!/usr/bin/python3

from game import *
import  random
import time
import sys, os
import socket
import select
import time
import re

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



def displayConfiguration(boats, shots=[], showBoats=True):
    Matrix = [[" " for x in range(WIDTH+1)] for y in range(WIDTH+1)]
    for i  in range(1,WIDTH+1):
        Matrix[i][0] = chr(ord("A")+i-1)
        Matrix[0][i] = i

    if showBoats:
        for i in range(NB_BOATS):
            b = boats[i]
            (w,h) = boat2rec(b)
            for dx in range(w):
                for dy in range(h):
                    Matrix[b.x+dx][b.y+dy] = str(i)

    for (x,y,stike) in shots:
        if stike:
            Matrix[x][y] = "X"
        else:
            Matrix[x][y] = "O"

    result = ""
    for y in range(0, WIDTH+1):
        if y == 0:
            l = "  "
        else:
            l = str(y)
            if y < 10:
                l = l + " "
        for x in range(1,WIDTH+1):
            l = l + str(Matrix[x][y]) + " "
        result += l + "\n"
    return result

""" display the game viewer by the player"""
def displayGame(game, player):
    otherPlayer = (player+1)%2
    return displayConfiguration(game.boats[player], game.shots[otherPlayer], showBoats=True) + displayConfiguration([], game.shots[player], showBoats=False)



""" Play a new random shot """
def randomNewShot(shots):
    (x,y) = (random.randint(1,10), random.randint(1,10))
    while not isANewShot(x,y,shots):
        (x,y) = (random.randint(1,10), random.randint(1,10))
    return (x,y)

def runServerMode():
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
                    #Envoyer la disposition de la partie
                    sJ0.send(displayGame(game, 0).encode("utf-8"))
                    sJ1.send(displayGame(game, 1).encode("utf-8"))

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

                if currentPlayer == J0 and sk == sJ0:
                    x = ord(rep[0].capitalize())-ord("A")+1
                    y = int(rep[1])
                    addShot(game, x, y, currentPlayer)
                    if gameOver(game) != -1:
                        displayGameOver(sJ0, sJ1, game)

                    sJ0.send("1".encode("utf-8"))
                    sJ1.send("1".encode("utf-8"))
                    time.sleep(1)
                    sJ0.send(displayGame(game, 0).encode("utf-8"))
                    sJ1.send(displayGame(game, 1).encode("utf-8"))
                    currentPlayer = (currentPlayer+1)%2
                elif currentPlayer == J1 and sk == sJ1:
                    x = ord(rep[0].capitalize())-ord("A")+1
                    y = int(rep[1])
                    addShot(game, x, y, currentPlayer)
                    if gameOver(game) != -1:
                        displayGameOver(sJ0, sJ1, game)

                    sJ0.send("0".encode("utf-8"))
                    sJ1.send("0".encode("utf-8"))
                    time.sleep(1)
                    sJ0.send(displayGame(game, 0).encode("utf-8"))
                    sJ1.send(displayGame(game, 1).encode("utf-8"))
                    currentPlayer = (currentPlayer+1)%2
                else:
                    print("WRONG")


                """
                elif currentPlayer == J0 and colDemandee and not ligneDemandee and gameOver(game) == -1:
                    rep = rep.capitalize()
                    x = ord(rep)-ord("A")+1
                    sJ0.send("quelle ligne ? \n".encode("utf-8"))
                    ligneDemandee = True
                elif currentPlayer == J0 and colDemandee and ligneDemandee:
                    y = int(rep)
                    addShot(game, x, y, currentPlayer)
                    print("gameOver = ", gameOver(game))
                    if gameOver(game) != -1:
                        displayGameOver(sJ0, sJ1, game)
                        continue
                    sJ0.send("======================\n".encode("utf-8"))
                    sJ1.send("======================\n".encode("utf-8"))
                    sJ0.send(displayGame(game, 0).encode("utf-8"))
                    sJ1.send(displayGame(game, 1).encode("utf-8"))
                    currentPlayer = (currentPlayer+1)%2
                    ligneDemandee = False
                    sJ1.send("quelle colonne ? ".encode("utf-8"))

                elif currentPlayer == J1 and colDemandee and not ligneDemandee and gameOver(game) == -1:
                    rep = rep.capitalize()
                    x = ord(rep)-ord("A")+1
                    sJ1.send("quelle ligne ? \n".encode("utf-8"))
                    ligneDemandee = True
                elif currentPlayer == J1 and colDemandee and ligneDemandee:
                    y = int(rep)
                    addShot(game, x, y, currentPlayer)
                    print("gameOver = ", gameOver(game))
                    if gameOver(game) != -1:
                        displayGameOver(sJ0, sJ1, game)
                        continue
                    sJ0.send("======================\n".encode("utf-8"))
                    sJ1.send("======================\n".encode("utf-8"))
                    sJ0.send(displayGame(game, 0).encode("utf-8"))
                    sJ1.send(displayGame(game, 1).encode("utf-8"))
                    currentPlayer = (currentPlayer+1)%2
                    ligneDemandee = False
                    sJ0.send("quelle colonne ? ".encode("utf-8"))
                """

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

def runClientMode(ServerAdress):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((sys.argv[1], 7777))

    #Recevoir son numero de joueur(0 ou 1)
    playerNum = client.recv(16).decode("utf-8")
    playerNum = int(playerNum)
    print("PLAYER NUM : ", playerNum)
    while True:
        #Recevoir le joueur actuel
        currentPlayer = client.recv(16).decode("utf-8")
        print("currentPlayer : ", currentPlayer)
        #Recevoir la disposition de la partie
        gameString = client.recv(2048).decode("utf-8")
        currentPlayer = int(currentPlayer)
        print("======================")
        print(gameString)

        if currentPlayer == playerNum:
            col = input("quelle colonne ? ")
            while len(col) != 1 or not re.compile("[a-jA-J]").match(col):
                #TEST valeur col valide
                print("PAS BON CARACTERE")
                col = input("quelle colonne ? ")
            lig = input("quelle ligne ? ")
            while len(lig) == 0 or len(lig) > 2 or not re.compile("(10|[1-9])").match(lig):
                #TEST valeur lig valide
                print("PAS BON CARACTERE")
                lig = input("quelle ligne ? ")
            client.send((col + lig).encode("utf-8"))
        else:
            print("L'autre joueur joue...")



if len(sys.argv) == 1:
    print("Lancement du mode Serveur")
    runServerMode()
else:
    print("Lancement du mode Client...")
    runClientMode(sys.argv[1])
