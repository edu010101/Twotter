from twotter.entitites import TwotterMessage, MessageType
import struct


def encode_message(message: TwotterMessage) -> bytes:
    """
    Codifica um objeto TwotterMessage em um objeto bytes.
    """
    username = message.username[:20].ljust(20, '\0')  
    text = message.text[:140].ljust(141, '\0')  

    text_size = len(text.encode('utf-8'))

    if type(message.message_type) == MessageType:
        message.message_type = message.message_type.value

    message = struct.pack('!IIII20s141s', message.message_type, message.origin_id, message.destination_id, text_size, username.encode('utf-8'), text.encode('utf-8'))

    return message


def decode_message(message: bytes) -> TwotterMessage:
    """
    Decodifica um objeto bytes em um objeto TwotterMessage.
    """
    msg_type, origin_id, destination_id, text_size, username, text = struct.unpack('!IIII20s141s', message)
    
    username = username.decode('utf-8').strip('\0')
    text = text.decode('utf-8').strip('\0')
    
    return TwotterMessage(msg_type, 
                          origin_id, 
                          destination_id, 
                          username, 
                          text)

def remove_control_characters(text):
    '''
    Remove caracteres que não são imprimíveis (ASCII ou Unicode)
    '''
    return ''.join(ch for ch in text if ch.isprintable())