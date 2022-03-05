from rich import print
from rich.table import Table

from os import environ
from socket import create_server, socket

from champlistloader import load_some_champs
from core import Champion, Match, Shape, Team

class GameServer:
    def __init__(self, address: str, port: int, buffer_size: int = 2048) -> None:
        self._address = address
        self._port = port
        self._buffer_size = buffer_size
        self._connections = {}

    def start(self):
        self._join_sock = create_server((self._address, self._port), reuse_port=True)

        self._accept()
    
    def shut_down(self):
        print("Stopping the server")
        for user in self._connections:
            self._connections[user].close()
        self._connections = {}
        quit()

    def _accept(self):

        conn, _ = self._join_sock.accept()
        self._join(conn)

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
                    sock.sendall('True'.encode())
                    for user in self._connections:
                        self._connections[user].sendall(f'{prompt} chose {name}!'.encode())
                    break

    def print_available_champs(champions: dict[Champion]) -> None:

        # Create a table containing available champions
        available_champs = Table(title='Available champions')

        # Add the columns Name, probability of rock, probability of paper and
        # probability of scissors
        available_champs.add_column("Name", style="cyan", no_wrap=True)
        available_champs.add_column("prob(:raised_fist-emoji:)", justify="center")
        available_champs.add_column("prob(:raised_hand-emoji:)", justify="center")
        available_champs.add_column("prob(:victory_hand-emoji:)", justify="center")

        # Populate the table
        for champion in champions.values():
            available_champs.add_row(*champion.str_tuple)

        print(available_champs)

    def print_match_summary(match: Match) -> None:

        EMOJI = {
            Shape.ROCK: ':raised_fist-emoji:',
            Shape.PAPER: ':raised_hand-emoji:',
            Shape.SCISSORS: ':victory_hand-emoji:'
        }

        # For each round print a table with the results
        for index, round in enumerate(match.rounds):

            # Create a table containing the results of the round
            round_summary = Table(title=f'Round {index+1}')

            # Add columns for each team
            round_summary.add_column("Red",
                                    style="red",
                                    no_wrap=True)
            round_summary.add_column("Blue",
                                    style="blue",
                                    no_wrap=True)

            # Populate the table
            for key in round:
                red, blue = key.split(', ')
                round_summary.add_row(f'{red} {EMOJI[round[key].red]}',
                                    f'{blue} {EMOJI[round[key].blue]}')
            print(round_summary)
            print('\n')

        # Print the score
        red_score, blue_score = match.score
        print(f'Red: {red_score}\n'
            f'Blue: {blue_score}')

        # Print the winner
        if red_score > blue_score:
            print('\n[red]Red victory! :grin:')
        elif red_score < blue_score:
            print('\n[blue]Blue victory! :grin:')
        else:
            print('\nDraw :expressionless:')

    def _main(self):

        players = []

        for user in self._connections:
            players.append(user)

        champions = load_some_champs()

        self.print_available_champs(champions)

        ## send champions to clients

        player1 = []
        player2 = []

        # Champion selection
        for _ in range(2):
            self.input_champion(f'[red]{players[0]}', self._connections[players[0]], champions, player1, player2)
            self.input_champion(f'[blue]{players[1]}', self._connections[players[1]], champions, player2, player1)

        # Match
        match = Match(
            Team([champions[name] for name in player1]),
            Team([champions[name] for name in player2])
        )
        match.play()

        # Print a summary
        self.print_match_summary(match)

        print("Game concluded...")
        self.shut_down


if __name__ == "__main__":
    host = '0.0.0.0'
    port = 5555
    server = GameServer(host, port)
    server.start()