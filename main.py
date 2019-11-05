#!/usr/bin/python3

from game import *
import  random
import time
import sys, os
import socket
import select

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
                    waitingPlayers = False
                    print("2 players connected : Let the game begins !")
                    sJ0 = clients[1]
                    sJ1 = s2
                    sJ1.send(displayGame(game, 1).encode("utf-8"))
                    sJ0.send(displayGame(game, 0).encode("utf-8"))

                    currentPlayer = 0
                    sJ0.send("quelle colonne ? ".encode("utf-8"))
                    colDemandee = True
                    ligneDemandee = False
            else:  #Commands reception
                r = sk.recv(1500)
                print(r)
                line = r.decode("utf-8")
                mots = line.split()
                rep = r.decode("utf-8")
                if r == b'':
                    print("Disconnection of the address " + sk.getsockname()[0])
                    sk.close()
                    clients.remove(sk)

                elif currentPlayer == J0 and not colDemandee and not ligneDemandee: # TOUR J0
                    sJ0.send("quelle colonne ? \n".encode("utf-8"))
                    colDemandee = True
                elif currentPlayer == J0 and colDemandee and not ligneDemandee:
                    rep.capitalize()
                    x = ord(rep)-ord("A")+1
                    sJ0.send("quelle ligne ? \n".encode("utf-8"))
                    colDemandee = True
                elif currentPlayer == J0 and colDemandee and ligneDemandee:
                    y = int(rep)
                    addShot(game, x, y, currentPlayer)
                    print("======================")
                    displayGame(game, 0)
                    currentPlayer = (currentPlayer+1)%2
                    colDemandee = False
                    ligneDemandee = False

                elif currentPlayer == J1 and not colDemandee and not ligneDemandee: # TOUR J1
                    sJ0.send("quelle colonne ? \n".encode("utf-8"))
                    colDemandee = True
                elif currentPlayer == J1 and colDemandee and not ligneDemandee:
                    rep.capitalize()
                    x = ord(rep)-ord("A")+1
                    sJ1.send("quelle ligne ? \n".encode("utf-8"))
                    colDemandee = True
                elif currentPlayer == J1 and colDemandee and ligneDemandee:
                    y = int(rep)
                    addShot(game, x, y, currentPlayer)
                    print("======================")
                    displayGame(game, 0)
                    currentPlayer = (currentPlayer+1)%2
                    colDemandee = False
                    ligneDemandee = False
    """
    currentPlayer = 0
    while gameOver(game) == -1:
        if currentPlayer == J0:
            x_char = input ("quelle colonne ? ")
            x_char.capitalize()
            x = ord(x_char)-ord("A")+1
            y = int(input ("quelle ligne ? "))
        else:
            (x,y) = randomNewShot(game.shots[currentPlayer])
            print("l'ordinateur joue ", chr(x+ord("A")-1), y)
            time.sleep(1)
        addShot(game, x, y, currentPlayer)
        print("======================")
        displayGame(game, 0)
        currentPlayer = (currentPlayer+1)%2
    print("game over")
    print("your grid :")
    displayGame(game, J0)
    print("the other grid :")
    displayGame(game, J1)

    if gameOver(game) == J0:
        print("You win !")
    else:
        print("you loose !")
    """

def runClientMode(ServerAdress):
    os.system("nc " + ServerAdress + " 7777")


if len(sys.argv) == 1:
    print("Lancement du mode Serveur")
    runServerMode()
else:
    runClientMode(sys.argv[1])
