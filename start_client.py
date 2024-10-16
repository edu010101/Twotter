import random

import streamlit as st

from twotter import TwotterClient
from twotter.ui.client_ui import TwotterClientUI
from twotter.config import SERVER_PORT, EMOJI_LIST


def main():
    if 'client_ui' not in st.session_state:
        st.title("Selecione seu ID e Usuário")
    
        input_placeholder = st.empty()
        with input_placeholder.container():
            server_host = st.text_input("Endereço IP do Servidor", value="localhost")
            client_id = st.number_input("Escolha seu ID", min_value=1, max_value=1000)
            EMOJI_LIST.insert(0, random.choice(EMOJI_LIST))
            username = st.selectbox("Selecione seu Usuário (emoji)", EMOJI_LIST)
            
            if st.button("Entrar no Twotter"):
                server_address = (server_host, SERVER_PORT)
                client = TwotterClient(server_address, client_id, username)
                st.session_state.client_ui = TwotterClientUI(client)
                input_placeholder.empty()  # Limpar o placeholder
                st.rerun()
    
    else:
        st.session_state.client_ui.run_chat_ui()



if __name__ == "__main__":
    main()
