import streamlit as st
import socket
import struct
import threading

from twotter.utils import decode_message, encode_message
from twotter.entitites import TwotterMessage, MessageType


class TwotterClient:
    def __init__(self, server_address, client_id, username):
        self.server_address = server_address
        self.client_id = client_id
        self.username = username[:20].ljust(20, '\0')  # Garantir que o nome tenha 20 caracteres
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cliente UDP
        self.received_messages = []

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

            message_type = message.message_type
            if message_type == MessageType.MESSAGE.value:
                self.received_messages.append(f"{message.username}: {message.text}")
                print("REEECEEEEEEEEEEEEEEEEBA")
                with st.chat_message(message.username):
                    st.write(message.text)


    def streamlit_ui(self):
        st.title("Cliente de Chat - UDP")

        # Campo de exibição das mensagens recebidas
        st.subheader("Mensagens recebidas:")
        for msg in self.received_messages:
            st.write(msg)

        # Campo de entrada para o envio de mensagem
        text = st.text_input("Digite sua mensagem", "")
        destination_id = st.number_input("ID do destinatário (0 para todos)", min_value=0, value=0)

        # Botão para enviar a mensagem
        if st.button("Enviar"):
            if text:
                self.send_message(text, destination_id)

        # Botão para desconectar e enviar a mensagem TCHAU
        if st.button("Sair"):
            self.send_bye()
            st.stop()

# Configuração do cliente e conexão com o servidor
server_address = ('localhost', 12345)  # Endereço do servidor
client_id = 1  # Identificador único do cliente
username = "Cliente1"  # Nome do usuário (máximo 20 caracteres)

# Instancia o cliente
client = TwotterClient(server_address, client_id, username)

# Iniciar thread para receber mensagens
threading.Thread(target=client.receive_messages, daemon=True).start()

# Enviar mensagem OI ao iniciar a sessão
client.send_hello()

# Exibe a interface
client.streamlit_ui()

with st.chat_message("user"):
    st.write("Hello 👋")

# import streamlit as st
# import socket
# import struct
# import threading

# # Configuração do cliente e conexão com o servidor
# server_address = ('localhost', 12345)  # Endereço do servidor
# client_id = 1  # Identificador único do cliente
# username = "Cliente1"  # Nome do usuário (máximo 20 caracteres)
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cliente UDP

# # Função para criar uma mensagem no formato correto
# def encode_message(msg_type, origin_id, destination_id, username, text):
#     username = username[:20].ljust(20, '\0')  # Garantir que o nome tenha 20 caracteres
#     text = text[:140].ljust(141, '\0')  # Garantir que o texto tenha 141 caracteres
#     text_size = len(text.encode('utf-8'))
#     message = struct.pack('!IIII20s141s', msg_type, origin_id, destination_id, text_size, username.encode('utf-8'), text.encode('utf-8'))
#     return message

# # Função para enviar uma mensagem OI para o servidor
# def send_hello():
#     msg = create_message(0, client_id, 0, username, '')
#     sock.sendto(msg, server_address)

# # Função para enviar uma mensagem TCHAU para o servidor
# def send_bye():
#     msg = create_message(1, client_id, 0, username, '')
#     sock.sendto(msg, server_address)

# # Função para enviar uma mensagem de texto
# def send_message(text, destination_id):
#     msg = create_message(2, client_id, destination_id, username, text)
#     sock.sendto(msg, server_address)

# # Função para decodificar mensagens recebidas
# def parse_message(data):
#     msg_type, origin_id, destination_id, text_size, username, text = struct.unpack('!IIII20s141s', data)
#     username = username.decode('utf-8').strip('\0')
#     text = text.decode('utf-8').strip('\0')
#     return msg_type, origin_id, destination_id, username, text

# # Variável global para armazenar as mensagens recebidas
# received_messages = []

# # Função para receber mensagens do servidor e atualizá-las em tempo real
# def receive_messages():
#     while True:
#         data, _ = sock.recvfrom(1024)  # Recebe mensagem UDP
#         msg_type, origin_id, destination_id, username, text = parse_message(data)
#         if msg_type == 2:  # Se for uma mensagem de texto
#             received_messages.append(f"{username}: {text}")
#             st.experimental_rerun()  # Atualiza a interface do Streamlit

# # Função que define a UI do Streamlit
# def streamlit_ui():
#     st.title("Cliente de Chat - UDP")

#     # Campo de exibição das mensagens recebidas
#     st.subheader("Mensagens recebidas:")
#     for msg in received_messages:
#         st.write(msg)

#     # Campo de entrada para o envio de mensagem
#     text = st.text_input("Digite sua mensagem", "")
#     destination_id = st.number_input("ID do destinatário (0 para todos)", min_value=0, value=0)

#     # Botão para enviar a mensagem
#     if st.button("Enviar"):
#         if text:
#             send_message(text, destination_id)

#     # Botão para desconectar e enviar a mensagem TCHAU
#     if st.button("Sair"):
#         send_bye()
#         st.stop()

# # Iniciar thread para receber mensagens
# threading.Thread(target=receive_messages, daemon=True).start()

# # Enviar mensagem OI ao iniciar a sessão
# send_hello()

# # Exibe a interface
# streamlit_ui()
