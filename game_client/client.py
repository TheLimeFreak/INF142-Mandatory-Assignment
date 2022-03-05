from rich import print
from rich.prompt import Prompt
from rich.table import Table

from socket import create_connection, timeout

class GameClient:
    def __init__(self, server: str, buffer_size: int = 2048) -> None:
        self._server = server
        self._port = 5555
        self._buffer_size = buffer_size

    def start(self):
        if self._register():
            self._main()

    def _register(self) -> bool:
        user = Prompt.ask('Username: ')
        while user:
            self._sock = create_connection((self._server, self._port), timeout=5)
            self._sock.sendall(user.encode())
            response = self._sock.recv(self._buffer_size).decode()
            print(response)
            if response == "Joined game":
                return True
        return False

    def input_champion(self):
        response = self._sock.recv(self._buffer_size).decode()
        if response == 'Choose champion: ':
            self._sock.sendall(Prompt.ask(f'{response}').encode())
        else:
            print(response)
            response = self._sock.recv(self._buffer_size).decode()
        self._sock.sendall(Prompt.ask(f'{response}').encode())
        response = self._sock.recv(self._buffer_size).decode()
        print(response)
        

    def _main(self) -> None:

        print('\n'
            'Welcome to [bold yellow]Team Local Tactics[/bold yellow]!'
            '\n'
            'Each player choose a champion each time.'
            '\n')

        ## recv champs from server
        
        print('\n')
        
        for _ in range(2):
            self.input_champion()

        print('\n')


        self._sock.close()



if __name__ == '__main__':
    server = '0.0.0.0'
    client = GameClient(server)
    client.start()