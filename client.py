#!/usr/bin/python3
# from game import *
import sys
import socket, pickle
import time
import re

from game import *


def main():
    try:
        serverAddress=""
        try:
            serverAddress=sys.argv[1]
        except:
            serverAddress=input("Adresse du serveur : ")

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try :
            server.connect((serverAddress, 7777))
            print("Connecté ! En attente du deuxième joueur...")
        except :
            print("ERROR : Server unknown")
            sys.exit(1)
    
        #Recevoir son numero de joueur(0 ou 1)
        playerNum = server.recv(16)
        playerNum = int(playerNum.decode("utf-8"))
        print("---LET THE GAME BEGINS---")
        
        endConnection = False
        while not endConnection:
            #Recevoir le joueur actuel
            currentPlayer = server.recv(16).decode("utf-8")
            # print("currentPlayer : ", currentPlayer)
            currentPlayer = int(currentPlayer)

            #Recevoir la disposition de la partie si la partie n'est pas finie
            if currentPlayer != -1:
                (boats, shotsPlayer, shotsOther) = pickle.loads(server.recv(1024))
                gameString = displayGame(boats, shotsPlayer, shotsOther)
                print("======================")
                print(gameString)

            if currentPlayer == playerNum:
                msg = input("Quelle ColonneLigne ? ")
                while not re.compile("[a-jA-J]{1}(10|[1-9]){1}$").match(msg):
                    #TEST valeur col valide
                    print("[Colonne][Ligne] ex : b" + str(random.randint(1,10)))
                    msg = input("Quelle ColonneLigne ? ")
                server.send(msg.encode("utf-8"))
            elif currentPlayer == -1:
                #Fin de partie
                print("Game over !")
                time.sleep(0.1)
                print("Ta grille : ")
                #Réception des grilles des 2 joueurs
                (myBoats, opponentBoats, shotsPlayer, shotsOther) = pickle.loads(server.recv(1024))

                myGrid = displayConfiguration(boats, shotsOther, showBoats=True)
                print(myGrid)
                time.sleep(0.1)
                opponentGrid = displayConfiguration(opponentBoats, shotsPlayer, showBoats=True)
                print("La grille de l'adversaire : ")
                print(opponentGrid)
                #Réception du gagnant
                winner = server.recv(16).decode("utf-8")
                winner = (int(winner))

                if winner == playerNum:
                    print("Wouhou tu as gagné")
                else:
                    print("C'est perdu")
                endConnection = True
            else:
                print("L'autre joueur joue...")
            print (server.recv(1024).decode("utf-8"))
    except KeyboardInterrupt:
        print("\nEndig game...")
        sys.exit(1)
    except ValueError:
        print("The other player disconnect, YOU WON")
        sys.exit(0)


""" display the game viewer by the player"""
def displayGame(boats, shotsPlayer, shotsOther):
    return displayConfiguration(boats, shotsOther, showBoats=True) + displayConfiguration([],shotsPlayer, showBoats=False)

main()
