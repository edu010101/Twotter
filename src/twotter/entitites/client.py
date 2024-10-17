import threading
import socket
import time

from twotter.utils import decode_message, encode_message
from twotter.entitites import TwotterMessage, MessageType


class TwotterClient:
    def __init__(self, server_address, client_id, username):
        self.server_address = server_address
        self.client_id = client_id
        self.username = username[:20].ljust(20, '\0') 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        self.received_messages = []
        print("Cliente iniciado")
        self.accepted = False
        self.start()

    def start(self):
        self.connect()
        threading.Thread(target=self.receive_messages, daemon=True).start()
        
    def connect(self):
        timeout = 5
        start_time = time.time()
        self.send_hello()
        while not self.accepted:
            if time.time() - start_time > timeout:
                print("Tempo de espera excedido")
                self.sock.close()
                raise TimeoutError("Tempo de espera excedido")
            
            data, _ = self.sock.recvfrom(1024)      
            message = decode_message(data)
            
            if message.message_type == MessageType.HELLO.value:
                print(f"Cliente {message.username} (ID {message.origin_id}) entrou")
                self.accepted = True
            elif message.message_type == MessageType.ERROR.value:
                print(f"Cliente {message.username} (ID {message.origin_id}) não foi aceito")
                self.sock.close()    
                raise ConnectionError("Já existe um cliente com esse ID, Conecte-se com outro ID")

    def send_hello(self):
        msg = encode_message(TwotterMessage(MessageType.HELLO, self.client_id, 0, self.username, ''))
        self.sock.sendto(msg, self.server_address)

    def send_bye(self):
        msg = encode_message(TwotterMessage(MessageType.BYE, self.client_id, 0, self.username, ''))
        self.sock.sendto(msg, self.server_address)

    def send_message(self, text, destination_id):
        msg = encode_message(TwotterMessage(MessageType.MESSAGE, self.client_id, destination_id, self.username, text))
        self.sock.sendto(msg, self.server_address)

    def receive_messages(self):
        while True:
            data, _ = self.sock.recvfrom(1024)
            
            message = decode_message(data)
            
            if self.accepted:
                message_type = message.message_type
                if message_type == MessageType.MESSAGE.value:
                    self.received_messages.append(message)    
            else:
                if message.message_type == MessageType.HELLO.value:
                    print(f"Cliente {message.username} (ID {message.origin_id}) entrou")
                    self.accepted = True
                elif message.message_type == MessageType.ERROR.value:
                    print(f"Cliente {message.username} (ID {message.origin_id}) não foi aceito")
                    self.send_bye()
                    self.sock.close()
    
    def __del__(self):
        self.send_bye()