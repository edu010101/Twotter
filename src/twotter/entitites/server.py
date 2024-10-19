import threading
import socket
import select
import time

from twotter.entitites import TwotterMessage, MessageType
from twotter.utils import encode_message, decode_message, logger
from twotter.config import SERVER_ADDRESS

SERVER_NAME = "assistant"
CLIENT_TIMEOUT_IN_SECONDS = 300

class TwotterServer:
    '''
    Classe que representa um servidor UDP que gerencia a comunicação entre clientes.

    Args:
        host (str): O endereço do servidor.
        port (int): A porta do servidor.

    Attributes:
        host (str): O endereço do servidor.
        port (int): A porta do servidor.
        sock (socket): O socket utilizado para comunicação.
        clients (dict): Dicionário que mapeia IDs de clientes para seus endereços.
    '''
    def __init__(self):
        self.clients = {}
        self.clients_times = {}

        self.start_time = time.time()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(SERVER_ADDRESS)
        logger.info("Servidor iniciado, aguardando mensagens...")

    def send_message_to_all(self, message):
        '''
        Envia uma mensagem para todos os clientes conectados.

        Args:
            message (bytes): A mensagem codificada a ser enviada.
        '''
        for client_addr in self.clients.values():
            self.sock.sendto(message, client_addr)

    def send_message_to_client(self, message, client_id):
        '''
        Envia uma mensagem específica para um cliente identificado por client_id.

        Args:
            message (bytes): A mensagem codificada a ser enviada.
            client_id (int): O ID do cliente destinatário.
        '''
        self.sock.sendto(message, self.clients[client_id])

    def periodic_status_message(self):
        '''
        Envia mensagens de status periodicamente para todos os clientes conectados.
        '''
        while True:
            time.sleep(60)
            num_clients = len(self.clients)
            status_msg = f"Servidor online, {num_clients} clientes conectados"
            message = encode_message(TwotterMessage(MessageType.MESSAGE, 0, 0, SERVER_NAME, status_msg))
            self.send_message_to_all(message)
            logger.info("Mensagem de status enviada: %s", status_msg)    
            self.remove_inactive_clients()
    
    def remove_inactive_clients(self):
        '''
        Remove clientes inativos por mais de 5 minutos.
        '''
        for client_id, last_time in self.clients_times.items():
            if time.time() - last_time > 300:
                del self.clients[client_id]
                del self.clients_times[client_id]
                logger.warning("Cliente %d removido por inatividade", client_id)

    def run(self):
        '''
        Inicia o servidor, entrando em um loop para processar mensagens recebidas.
        '''
        threading.Thread(target=self.periodic_status_message, daemon=True).start()

        while True:
            readable, _, _ = select.select([self.sock], [], [], 1)
            
            if readable:
                data, client_address = self.sock.recvfrom(1024)
                message = decode_message(data)
                self.handle_message(message, client_address, data)

    def handle_message(self, message, client_address, data):
        '''
        Despacha a mensagem recebida para o manipulador apropriado com base no tipo de mensagem.

        Args:
            message (TwotterMessage): A mensagem recebida.
            data (bytes): A mensagem codificada recebida.
            client_address (tuple): O endereço do cliente que enviou a mensagem.
        '''
        if message.message_type == 0:  # OI
            self.handle_oi_message(message, client_address)
        elif message.message_type == 1:  # TCHAU
            self.handle_tchau_message(message)
        elif message.message_type == 2:  # MSG
            self.handle_msg_message(message, data, client_address)
        elif message.message_type == 3:  # ERRO
            self.handle_error_message(message)
        elif message.message_type == 4: # GET_ONLINE_CLIENTS
            self.handle_get_online_clients_message(message, client_address)

    def handle_oi_message(self, message, client_address):
        '''
        Trata mensagens do tipo HELLO, registrando o cliente no servidor.

        Args:
            message (TwotterMessage): A mensagem de saudação recebida.
            client_address (tuple): O endereço do cliente que enviou a mensagem.
        '''
        if message.origin_id not in self.clients:
            self.clients[message.origin_id] = client_address
            self.clients_times[message.origin_id] = time.time()
            logger.info("Cliente %s (ID %d) entrou do endereço %s", message.username, message.origin_id, client_address)
            response = encode_message(TwotterMessage(MessageType.HELLO, 0, message.origin_id, message.username, ''))
            self.sock.sendto(response, client_address)
        else:
            logger.info("Cliente %d já está conectado", message.origin_id)
            response = encode_message(TwotterMessage(MessageType.ERROR, 0, message.origin_id, SERVER_NAME, "ID de cliente já está conectado."))
            self.update_client_timer(message.origin_id)
            self.sock.sendto(response, client_address)

    def handle_tchau_message(self, message):
        '''
        Trata mensagens do tipo BYE, removendo o cliente do servidor.

        Args:
            message (TwotterMessage): A mensagem de despedida recebida.
        '''
        if message.origin_id in self.clients:
            del self.clients[message.origin_id]
            logger.info("Cliente %s (ID %d) saiu.", message.username, message.origin_id)

    def handle_msg_message(self, message, data, client_address):
        '''
        Trata mensagens do tipo MESSAGE, enviando-as ao destinatário ou a todos os clientes.

        Args:
            message (TwotterMessage): A mensagem recebida.
            data (bytes): A mensagem codificada recebida.
            client_address (tuple): O endereço do cliente que enviou a mensagem.
        '''
        if message.origin_id in self.clients:
            if message.destination_id == 0:
                self.send_message_to_all(data)
                logger.info("Mensagem de %s enviada para todos os clientes", message.username)
            else:
                if message.destination_id in self.clients:
                    self.send_message_to_client(data, message.destination_id)
                    logger.info("Mensagem de %s enviada para %d", message.username, message.destination_id)
                else:
                    error_msg = encode_message(TwotterMessage(MessageType.ERROR, 0, message.origin_id, SERVER_NAME, "Destinatário não encontrado."))
                    self.sock.sendto(error_msg, client_address)
        else:
            logger.warning("Mensagem de origem inválida de %s", client_address)

    def handle_error_message(self, message):
        '''
        Trata mensagens do tipo ERROR, registrando o erro.

        Args:
            message (TwotterMessage): A mensagem de erro recebida.
        '''
        logger.error("Erro: %s", message.text)

    def handle_get_online_clients_message(self, message, client_address):
        '''
        Trata mensagens do tipo GET_ONLINE_CLIENTS, enviando uma lista de clientes online.

        Args:
            message (TwotterMessage): A mensagem recebida.
            client_address (tuple): O endereço do cliente que enviou a mensagem.
        '''
        online_clients = list(self.clients.keys())
        online_clients = [str(client) for client in online_clients]
        online_clients = ', '.join(online_clients)

        response = encode_message(TwotterMessage(MessageType.GET_ONLINE_CLIENTS, 0, message.origin_id, SERVER_NAME, online_clients))
        self.sock.sendto(response, client_address)
        logger.info("Lista de clientes online enviada para %d", message.origin_id)

    def update_client_timer(self, client_id):
        '''
        Atualiza o tempo de inatividade do cliente identificado por client_id.

        Args:
            client_id (int): O ID do cliente.
        '''
        self.clients_times[client_id] = time.time()
                    
