from dataclasses import dataclass
from enum import Enum

@dataclass
class TwotterMessage:
    """
    TwotterMessage is a dataclass that represents a message in Twotter.
    The Username has a maximum length of 20 characters.
    The Text has a maximum length of 140 characters.
    """
    message_type: int
    origin_id: int
    destination_id: int
    username: str
    text: str


class MessageType(Enum):
    """
    MessageType is an Enum that represents the type of a TwotterMessage.
    """
    HELLO = 0
    BYE = 1
    MESSAGE = 2
    ERROR = 3