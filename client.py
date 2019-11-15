#!/usr/bin/python3
# from game import *
import sys
import socket, pickle
import time
import re

from game import *


def main():
    serverAddress=""
    try:
        serverAddress=sys.argv[1]
    except Exception as e:
        serverAddress=input("Adresse du serveur : ")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((serverAddress, 7777))

    #Recevoir son numero de joueur(0 ou 1)
    playerNum = server.recv(16).decode("utf-8")
    playerNum = int(playerNum)
    print("PLAYER NUM : ", playerNum)
    endConnection = False
    while not endConnection:
        #Recevoir le joueur actuel
        currentPlayer = server.recv(16).decode("utf-8")
        print("currentPlayer : ", currentPlayer)
        currentPlayer = int(currentPlayer)

        #Recevoir la disposition de la partie si la partie n'est pas finie
        if currentPlayer != -1:
            (boats, shotsPlayer, shotsOther) = pickle.loads(server.recv(2048))
            gameString = displayGame(boats, shotsPlayer, shotsOther)
            print("======================")
            print(gameString)

        if currentPlayer == playerNum:
            col = input("Quelle colonne ? ")
            while len(col) != 1 or not re.compile("[a-jA-J]").match(col):
                #TEST valeur col valide
                print("Caracteres valides : [a-jA-J]")
                col = input("Quelle colonne ? ")
            lig = input("Quelle ligne ? ")
            while len(lig) == 0 or len(lig) > 2 or not re.compile("(10|[1-9])").match(lig):
                #TEST valeur lig valide
                print("Caracteres valides : [1-10]")
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
            winner = (int(winner)+1)%2
            #La valeur de winner est l'inverse de celle envoyer par le serveur (quand 1 gagne, le serveur envoie 1 et le client recoit 0)
            #sûrement une histoire de bit
            if winner == playerNum:
                print("Wouhou tu as gagné")
            else:
                print("C'est perdu")
            endConnection = True
        else:
            print("L'autre joueur joue...")


""" display the game viewer by the player"""
def displayGame(boats, shotsPlayer, shotsOther):
    return displayConfiguration(boats, shotsOther, showBoats=True) + displayConfiguration([],shotsPlayer, showBoats=False)

main()
