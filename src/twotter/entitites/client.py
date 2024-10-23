import threading
import socket
import time

from twotter.utils import decode_message, encode_message
from twotter.entitites import TwotterMessage, MessageType


class TwotterClient:   
    '''
    Classe que representa um cliente que se conecta a um servidor UDP.

    Args:
        server_address (tuple): O endereço do servidor.
        client_id (int): O ID do cliente.
        username (str): O nome de usuário do cliente.

    Attributes:
        server_address (tuple): O endereço do servidor.
        client_id (int): O ID do cliente.
        username (str): O nome de usuário do cliente.
        sock (socket): O socket utilizado para comunicação.
        received_messages (list): A lista de mensagens recebidas.
        accepted (bool): Status de aceitação do cliente pelo servidor.
    '''
    def __init__(self, server_address, client_id, username):
        self.server_address = server_address
        self.client_id = client_id
        self.username = username[:20].ljust(20, '\0') 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        self.received_messages = []
        self.online_users = ""
        print("Cliente iniciado")
        self.accepted = False
        self.start()

    def start(self):
        '''
        Inicia o cliente, conectando-se ao servidor e iniciando a thread para receber mensagens.
        '''
        self.connect()
        threading.Thread(target=self.receive_messages, daemon=True).start()
        
    def connect(self):
        '''
        Conecta o cliente ao servidor enviando uma mensagem de saudação e aguardando aceitação.

        Raises:
            TimeoutError: Se o tempo de espera para aceitação exceder o limite.
            ConnectionError: Se o ID do cliente já estiver em uso.
        '''
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
            
            if int(message.message_type) == MessageType.HELLO.value:
                print(f"Cliente {message.username} (ID {message.origin_id}) entrou")
                self.accepted = True
            elif int(message.message_type) == MessageType.ERROR.value:
                print(f"Cliente {message.username} (ID {message.origin_id}) não foi aceito")
                self.sock.close()    
                raise ConnectionError("Já existe um cliente com esse ID, por favor, conecte-se com outro ID")
            else:
                print("Mensagem inesperada", message)   
                raise ConnectionError("Mensagem inesperada")
            
    def send_hello(self):
        '''
        Envia uma mensagem de saudação (HELLO) ao servidor.
        '''
        msg = encode_message(TwotterMessage(MessageType.HELLO, self.client_id, 0, self.username, ''))
        self.sock.sendto(msg, self.server_address)

    def send_bye(self):
        '''
        Envia uma mensagem de despedida (BYE) ao servidor.
        '''
        msg = encode_message(TwotterMessage(MessageType.BYE, self.client_id, 0, self.username, ''))
        self.sock.sendto(msg, self.server_address)

    def send_message(self, text, destination_id):
        '''
        Envia uma mensagem de texto a outro cliente através do servidor.

        Args:
            text (str): O texto da mensagem a ser enviada.
            destination_id (int): O ID do cliente destinatário.
        '''
        msg = encode_message(TwotterMessage(MessageType.MESSAGE, self.client_id, destination_id, self.username, text))
        self.sock.sendto(msg, self.server_address)
    
    def send_get_online_clients(self):
        '''
        Envia uma mensagem ao servidor solicitando a lista de clientes online.
        '''
        msg = encode_message(TwotterMessage(MessageType.GET_ONLINE_CLIENTS, self.client_id, 0, self.username, ''))
        self.sock.sendto(msg, self.server_address)

    def receive_messages(self):
        '''
        Recebe mensagens do servidor e processa-as conforme o tipo de mensagem.
        '''
        while True:
            data, _ = self.sock.recvfrom(1024)
            
            message = decode_message(data)
            
            if self.accepted: # Se o cliente foi aceito
                message_type = message.message_type
                if message_type == MessageType.MESSAGE.value:
                    self.received_messages.append(message)   

                elif message_type == MessageType.GET_ONLINE_CLIENTS.value:
                    self.online_users = message.text
            
                elif message_type == MessageType.HELLO.value:
                    self.send_hello()
                    
            else: # Esperando aceitação
                if message.message_type == MessageType.HELLO.value:
                    print(f"Cliente {message.username} (ID {message.origin_id}) entrou")
                    self.accepted = True
                elif message.message_type == MessageType.ERROR.value:
                    print(f"Cliente {message.username} (ID {message.origin_id}) não foi aceito")
                    self.send_bye()
                    self.sock.close()
    
    def __del__(self):
        self.send_bye()