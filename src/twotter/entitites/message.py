from dataclasses import dataclass
from enum import Enum

@dataclass
class TwotterMessage:
    """
    TwotterMessage é uma dataclass que representa uma mensagem no Twotter.
    O Nome de Usuário tem um comprimento máximo de 20 caracteres.
    O Texto tem um comprimento máximo de 140 caracteres.
    """
    message_type: int
    origin_id: int
    destination_id: int
    username: str
    text: str

    def __str__(self) -> str:
        return f"TwotterMessage({self.message_type}, {self.origin_id}, {self.destination_id}, {self.username}, {self.text})"

class MessageType(Enum):
    """
    MessageType é um Enum que representa o tipo de uma TwotterMessage.
    """
    HELLO = 0
    BYE = 1
    MESSAGE = 2
    ERROR = 3
    GET_ONLINE_CLIENTS = 4