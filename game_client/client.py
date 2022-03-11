from rich import print
from rich.prompt import Prompt
from rich.table import Table

from socket import create_connection

class GameClient:
    def __init__(self, server: str, port: int, buffer_size: int = 2048) -> None:
        self._server = server
        self._port = port
        self._buffer_size = buffer_size

    def start(self):
        if self._register():
            self._main()

    def _register(self) -> bool:
        user = Prompt.ask('Username')
        while user:
            self._sock = create_connection((self._server, self._port))
            self._sock.sendall(user.encode())
            response = self._sock.recv(self._buffer_size).decode()
            print(response)
            if response == "Joined game":
                return True
        return False

    def print_available_champs(self):
        # Create a table containing available champions
        available_champs = Table(title='Available champions')

        # Add the columns Name, probability of rock, probability of paper and
        # probability of scissors
        available_champs.add_column("Name", style="cyan", no_wrap=True)
        available_champs.add_column("prob(:raised_fist-emoji:)", justify="center")
        available_champs.add_column("prob(:raised_hand-emoji:)", justify="center")
        available_champs.add_column("prob(:victory_hand-emoji:)", justify="center")

        while True:
            response = self._sock.recv(self._buffer_size).decode()
            if response == 'done':
                print(available_champs)
                break
            else:
                a, b, c, d = response.split(sep='|')
                available_champs.add_row(a, b, c, d)
                self._sock.sendall('ok'.encode())

    def input_champion(self):
        while True:
            response = self._sock.recv(self._buffer_size).decode()
            if response == 'Choose champion: ':
                self._sock.sendall(Prompt.ask(f'{response}').encode())
            elif response == 'done':
                break
            else:
                print(response)
    
    def print_match_summary(self):
        while True:
            response = self._sock.recv(self._buffer_size).decode()
            self._sock.sendall('ok'.encode())
            if response == 'table':
                # Create a table containing the results of the round
                round_summary = Table(title=self._sock.recv(self._buffer_size).decode())
                # Add columns for each team
                round_summary.add_column("Red",
                                        style="red",
                                        no_wrap=True)
                round_summary.add_column("Blue",
                                        style="blue",
                                        no_wrap=True)
                
                self._sock.sendall('ok'.encode())
                # Populate the table
                while True:
                    table_response = self._sock.recv(self._buffer_size).decode()
                    if table_response == 'done':
                        self._sock.sendall('ok'.encode())
                        break
                    else:
                        self._sock.sendall('ok'.encode())
                        round_summary.add_row(response,self._sock.recv(self._buffer_size).decode())
                        self._sock.sendall('ok'.encode())
                print(round_summary)
                print('\n')

            elif response == 'done':
                break
            else:
                print(response)
        

    def _main(self) -> None:

        print('\n'
            'Welcome to [bold yellow]Team Local Tactics[/bold yellow]!'
            '\n'
            'Each player choose a champion each time.'
            '\n')

        self.print_available_champs()
        
        print('\n')
        
        self.input_champion()

        print('\n')

        self.print_match_summary()

        self._sock.close()

if __name__ == '__main__':
    server = 'localhost'
    port = 5555
    client = GameClient(server, port)
    client.start()