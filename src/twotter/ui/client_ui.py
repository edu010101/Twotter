import time

import streamlit as st

from twotter import TwotterClient


class TwotterClientUI:
    def __init__(self, client: TwotterClient):
        self.client = client

    def write_received_message(self):
        with self.messages:
            for msg in self.client.received_messages:
                msg_text = msg.text
                msg_username = msg.username
                destiny_id = msg.destination_id
                origin_id = msg.origin_id
                if destiny_id == 0:
                    destiny_id = "Para Todos"
                elif origin_id != self.client.client_id:
                    destiny_id = origin_id
                elif destiny_id == self.client.client_id:
                    destiny_id = "Você"
                st.chat_message(msg_username).write(f"{destiny_id}: {msg_text}")

    def setup_sidebar(self):
        with st.sidebar:
            st.write(f"Seu Usuário: {self.client.username}")
            st.write(f"Seu ID no servidor: {self.client.client_id}")
            self.destination_id = st.number_input("ID do destinatário (0 para todos)", min_value=0, value=0)
            self.setup_exit_button()
    
    def setup_chat_input(self):
        chat_input_placeholder = st.empty()
        if prompt := chat_input_placeholder.chat_input("Digite Algo"):
            self.client.send_message(prompt, int(self.destination_id))
            if self.destination_id != 0 and self.client.client_id != self.destination_id:
                self.client.send_message(prompt, int(self.client.client_id))
    
    def setup_exit_button(self):
        exit_button_placeholder = st.sidebar.empty()
        with exit_button_placeholder:
            if st.button("Sair"):
                self.client.send_bye()
                st.error("Você saiu do twotter. Reinicia a página para entrar novamente.")
                st.stop()
                
    def run_chat_ui(self):
        st.title("Twotter Chat")
        self.setup_sidebar()
        self.messages = st.container()
        self.write_received_message()
        self.setup_chat_input()
        
        time.sleep(0.4)
        st.rerun()