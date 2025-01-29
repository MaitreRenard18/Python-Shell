import socket
import sys
from threading import Thread

import rsa
from colorama import Fore

from utils import frame_text


class Session:
    def __init__(self, server: "Server", client_socket: socket.socket):
        super().__init__()
        self.server = server
        self.socket = client_socket
        
        # Send server public key
        public_key_pem = self.server.public_key.save_pkcs1(format='PEM') # Encode public key
        self.socket.send(len(public_key_pem).to_bytes(4, "big")) # Send public key length
        self.socket.send(public_key_pem) # Send public key
        
        # Receive client public key
        size = int.from_bytes(self.socket.recv(4), "big")
        public_key_pem = self.socket.recv(size)
        self.client_key = rsa.PublicKey.load_pkcs1(public_key_pem, format='PEM')
    
        # Receive username
        self.username = self.recv()
    
    def recv(self):
        size = int.from_bytes(self.socket.recv(4), "big")
        return rsa.decrypt(self.socket.recv(size), self.server.private_key).decode()
    
    def send(self, message: str | bytes):
        if isinstance(message, str):
            message = message.encode()
        
        encrypted_message = rsa.encrypt(message, self.client_key)
        self.socket.send(len(encrypted_message).to_bytes(4, "big"))
        self.socket.send(encrypted_message)


class Server:
    DEFAULT_PORT = 621
    
    def __init__(self, port: int = DEFAULT_PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostname(), port))
        self.socket.listen(5)
        
        self.public_key, self.private_key = rsa.newkeys(2048)
        
        self.sessions = {}
        
        self.accept_thread = Thread(target=self.accept)
        self.accept_thread.start()
        
        while True:
            command = input(">>> ")
            args = command.split(" ")
            
            if len(args) == 0:
                continue
                
            method = getattr(self, f"_command_{args[0]}", self._command_unknown)
            method(*args)
    
    def accept(self):
        while True:
            (clientsocket, _) = self.socket.accept()
            session = Session(self, clientsocket)
            self.sessions[session.username] = session
    
    def _command_help(self, *args, **kwargs):
        frame_text(
            "• list - List connected users",
            "• send <username> <message> - Send message to user",
            "• clear - Clear terminal",
            "• exit - Exit server",
            title="Commands",
            color=Fore.CYAN,
        )
    
    def _command_list(self, *args, **kwargs):
        frame_text(
            *[f"• {username}" for username in self.sessions],
            title="Connected users",
            color=Fore.CYAN,
        )
    
    def _command_send(self, *args, **kwargs):
        if len(args) < 3:
            frame_text("Usage: send <username> <message>", title="Error", color=Fore.RED)
            return
        
        username = args[1]
        message = " ".join(args[2:])
        
        if username not in self.sessions:
            frame_text("User not found", title="Error", color=Fore.RED)
            return
        
        self.sessions[username].send(message)
        frame_text(f'Successfully sent "{message}"', title="Success", color=Fore.GREEN)
        frame_text(self.sessions[username].recv(), title="Response", color=Fore.MAGENTA)
    
    def _command_exit(self, *args, **kwargs):
        sys.exit(0)
    
    def _command_clear(self, *args, **kwargs):
        print("\033[H\033[J")
    
    def _command_unknown(self, *args, **kwargs):
        frame_text("Unknown command", title="Error", color=Fore.RED)


if __name__ == "__main__":
    server = Server()
