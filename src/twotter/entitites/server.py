import socket
import logging
import select
import time
import threading

from twotter.entitites import TwotterMessage
from twotter.utils import encode_message, decode_message, logger


SERVER_ADDRESS = ('localhost', 12345)


class TwotterServer:
    def __init__(self):
        self.clients = {}
        
        self.start_time = time.time()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(SERVER_ADDRESS)
        logger.info("Servidor iniciado, aguardando mensagens...")

    def send_message_to_all(self, message):
        for client_addr in self.clients.values():
            self.sock.sendto(message, client_addr)

    def send_message_to_client(self, message, client_id):
        self.sock.sendto(message, self.clients[client_id])

    def periodic_status_message(self):
        while True:
            time.sleep(60)  # Espera 1 minuto
            num_clients = len(self.clients)
            uptime = int(time.time() - self.start_time)
            status_msg = f"Servidor online, {num_clients} clientes conectados, uptime: {uptime} segundos"
            message = encode_message(TwotterMessage(2, 0, 0, "Servidor", status_msg))
            self.send_message_to_all(message)
            logger.info("Mensagem de status enviada: %s", status_msg)

    def run(self):
        threading.Thread(target=self.periodic_status_message, daemon=True).start()

        while True:
            readable, _, _ = select.select([self.sock], [], [], 1)
            
            if readable:
                data, client_address = self.sock.recvfrom(1024)
                message = decode_message(data)
                self.handle_message(message, client_address, data)

    def handle_message(self, message, client_address, data):
        if message.message_type == 0:  # OI
            self.handle_oi_message(message, client_address)
        elif message.message_type == 1:  # TCHAU
            self.handle_tchau_message(message)
        elif message.message_type == 2:  # MSG
            self.handle_msg_message(message, data, client_address)
        elif message.message_type == 3:  # ERRO
            self.handle_error_message(message)

    def handle_oi_message(self, message, client_address):
        self.clients[message.origin_id] = client_address
        logger.info("Cliente %s (ID %d) entrou do endereço %s", message.username, message.origin_id, client_address)
        response = encode_message(TwotterMessage(0, message.origin_id, 0, message.username, ''))
        self.sock.sendto(response, client_address)

    def handle_tchau_message(self, message):
        if message.origin_id in self.clients:
            del self.clients[message.origin_id]
            logger.info("Cliente %s (ID %d) saiu.", message.username, message.origin_id)

    def handle_msg_message(self, message, data, client_address):
        if message.origin_id in self.clients:
            if message.destination_id == 0:
                self.send_message_to_all(data)
            else:
                if message.destination_id in self.clients:
                    self.send_message_to_client(data, message.destination_id)
                else:
                    error_msg = encode_message(TwotterMessage(3, 0, message.origin_id, "Servidor", "Destinatário não encontrado."))
                    self.sock.sendto(error_msg, client_address)
        else:
            logger.warning("Mensagem de origem inválida de %s", client_address)

    def handle_error_message(self, message):
        logger.error("Erro: %s", message.text)

                    
