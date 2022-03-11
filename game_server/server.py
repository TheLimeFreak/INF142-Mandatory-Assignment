from typing import Collection
import pymongo
import os

from pymongo import MongoClient
from time import sleep
from dotenv import load_dotenv
from socket import create_server, socket

from core import Champion, Match, Shape, Team

class GameServer:
    def __init__(self, address: str, port: int, buffer_size: int = 2048) -> None:
        self._address = address
        self._port = port
        self._buffer_size = buffer_size
        self._connections = {}

    def connect_db(self) -> Collection:
        print(f'PyMongo version: {pymongo.version}')
        print('Connecting to MongoDB...')

        load_dotenv()

        username = os.environ.get("USER")
        password = os.environ.get("PASS")
        clusterName = "inf142-mandatory-assign"

        # Connect to you cluster
        client = MongoClient('mongodb+srv://' + username + ':' + password + '@' + clusterName + '.awcxl.mongodb.net/demo-db?retryWrites=true&w=majority')

        database = client.INF142
        return database.champion

    def start(self):
        print('Loading champions...')
        self.champions = self.load_champ_db()

        print('Starting server...')
        self._join_sock = create_server((self._address, self._port))

        self._accept()
    
    def shut_down(self):
        print("Stopping the server")

        for user in self._connections:
            self._connections[user].sendall('stopping server'.encode())

        sleep(3)

        for user in self._connections:
            self._connections[user].close()
        self._connections = {}
        quit()

    def _accept(self):
        print('Rady for connections')
        for _ in range(2):
            conn, _ = self._join_sock.accept()
            self._join(conn)

        self._main()

    def _join(self, conn):
        data = conn.recv(self._buffer_size)
        user = data.decode()
        print(f"{user} joined the game!")
        conn.sendall("Joined game".encode())
        self._connections[user] = conn
    
    def input_champion(self,
                       prompt: str,
                       sock: socket,
                       champions: dict[Champion],
                       player1: list[str],
                       player2: list[str]) -> None:

        # Prompt the player to choose a champion and provide the reason why
        # certain champion cannot be selected
        while True:
            sock.sendall('Choose champion: '.encode())
            match sock.recv(self._buffer_size).decode():
                case name if name not in champions:
                    sock.sendall(f'The champion {name} is not available. Try again.'.encode())
                case name if name in player1:
                    sock.sendall(f'{name} is already in your team. Try again.'.encode())
                case name if name in player2:
                    sock.sendall(f'{name} is in the enemy team. Try again.'.encode())
                case _:
                    player1.append(name)
                    for user in self._connections:
                        self._connections[user].sendall(f'{prompt} chose {name}!'.encode())
                    break

    def send_available_champs(self, champions: dict[Champion]) -> None:
        
        print('Sending available champions...')

        for champion in champions.values():
            for user in self._connections:
                self._connections[user].sendall(f'{champion}'.encode())
                _ = self._connections[user].recv(self._buffer_size)
        
        for user in self._connections:
            self._connections[user].sendall('done'.encode())
        
        

    def send_match_summary(self, match: Match) -> None:

        EMOJI = {
            Shape.ROCK: ':raised_fist-emoji:',
            Shape.PAPER: ':raised_hand-emoji:',
            Shape.SCISSORS: ':victory_hand-emoji:'
        }


        # For each round send a table with the results
        for index, round in enumerate(match.rounds):
            print(f'Sending round {index}')
            for user in self._connections:
                self._connections[user].sendall('table'.encode())
                _ = self._connections[user].recv(self._buffer_size)
                self._connections[user].sendall(f'Round {index+1}'.encode())
                _ = self._connections[user].recv(self._buffer_size)

                # Send the table
                for key in round:
                    red, blue = key.split(', ')
                    self._connections[user].sendall(f'{red} {EMOJI[round[key].red]}'.encode())
                    _ = self._connections[user].recv(self._buffer_size)
                    self._connections[user].sendall(f'{blue} {EMOJI[round[key].blue]}'.encode())
                    _ = self._connections[user].recv(self._buffer_size)
                
                self._connections[user].sendall('done'.encode())
                _ = self._connections[user].recv(self._buffer_size)
                sleep(1)

        for user in self._connections:
            # Send the score
            red_score, blue_score = match.score
            self._connections[user].sendall(f'Red: {red_score}\nBlue: {blue_score}'.encode())

            # Send the winner
            if red_score > blue_score:
                self._connections[user].sendall('\n[red]Red victory! :grin:'.encode())
            elif red_score < blue_score:
                self._connections[user].sendall('\n[blue]Blue victory! :grin:'.encode())
            else:
                self._connections[user].sendall('\nDraw :expressionless:'.encode())

            _ = self._connections[user].recv(self._buffer_size)
            sleep(1)
            self._connections[user].sendall('done'.encode())
            _ = self._connections[user].recv(self._buffer_size)

    def load_champ_db(self) -> dict[str, Champion]:
        collection = self.connect_db()
        
        champions = {}
        for champion in collection.find():
            champ = Champion(champion['name'], champion['rock'], champion['paper'], champion['scissors'])
            champions[champ.name] = champ
            print(f'Loaded: {champ.name}')
        return champions


    def _main(self):

        players = []

        for user in self._connections:
            players.append(user)

        sleep (3)

        ## send champions to clients
        self.send_available_champs(self.champions)

        player1 = []
        player2 = []

        # Champion selection
        for _ in range(2):
            self.input_champion(f'[red]{players[0]}', self._connections[players[0]], self.champions, player1, player2)
            self.input_champion(f'[blue]{players[1]}', self._connections[players[1]], self.champions, player2, player1)

        sleep(3)

        for user in self._connections:
            self._connections[user].sendall('done'.encode())

        print('Playing match...')
        for user in self._connections:
            self._connections[user].sendall('\nPlaying match...\n'.encode())
            _ = self._connections[user].recv(self._buffer_size)

        # Match
        match = Match(
            Team([self.champions[name] for name in player1]),
            Team([self.champions[name] for name in player2])
        )
        match.play()

        # Send a summary
        self.send_match_summary(match)

        print("Game concluded...")
        self.shut_down


if __name__ == "__main__":
    host = 'localhost'
    port = 5555
    server = GameServer(host, port)
    server.start()