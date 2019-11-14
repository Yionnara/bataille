#!/usr/bin/python3
# from game import *
import sys
import socket, pickle
import re

from game import *


def main():
    serverAddress=""
    try:
        serverAddress=sys.argv[1]
    except Exception as e:
        serverAddress=input("Enter Server Address : ")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((serverAddress, 7777))

    #Recevoir son numero de joueur(0 ou 1)
    playerNum = server.recv(16).decode("utf-8")
    playerNum = int(playerNum)
    print("PLAYER NUM : ", playerNum)
    while True:
        #Recevoir le joueur actuel
        currentPlayer = server.recv(16).decode("utf-8")
        print("currentPlayer : ", currentPlayer)
        currentPlayer = int(currentPlayer)

        #Recevoir la disposition de la partie si la partie n'est pas finie
        if currentPlayer != -1:
            (boats, shotsP, shotsF) = pickle.loads(server.recv(4096))
            gameString = displayGame(boats, shotsP, shotsF)
            print("======================")
            print(gameString)

        if currentPlayer == playerNum:
            col = input("Quelle colonne ? ")
            while len(col) != 1 or not re.compile("[a-jA-J]").match(col):
                #TEST valeur col valide
                print("PAS BON CARACTERE")
                col = input("Quelle colonne ? ")
            lig = input("Quelle ligne ? ")
            while len(lig) == 0 or len(lig) > 2 or not re.compile("(10|[1-9])").match(lig):
                #TEST valeur lig valide
                print("PAS BON CARACTERE")
                lig = input("Quelle ligne ? ")
            server.send((col + lig).encode("utf-8"))
        elif currentPlayer == -1:
            #Fin de partie
            print("Game over !")
            time.sleep(0.7)
            print("Ta grille : ")
            #Réception de ma grille
            myGrid = server.recv(2048).decode("utf-8")
            print(myGrid)
            time.sleep(1)
            #Réception de la grille du joueur adverse
            opponentGrid = server.recv(2048).decode("utf-8")
            print("La grille de l'adversaire : ")
            print(opponentGrid)

            #Réception du gagnant
            winner = server.recv(16).decode("utf-8")
            winner = int(winner)
            print("WINNER : ", winner)
            if winner == playerNum:
                print("Wouhou tu as gagné")
            else:
                print("C'est perdu")

        else:
            print("L'autre joueur joue...")


""" display the game viewer by the player"""
def displayGame(boats, shotsP, shotsF):
    return displayConfiguration(boats, shotsF, showBoats=True) + displayConfiguration([],shotsP, showBoats=False)

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

main()