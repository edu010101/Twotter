from twotter.entitites import TwotterMessage    
import struct


def encode_message(message: TwotterMessage) -> bytes:
    """
    Encodes a TwotterMessage object into a bytes object.
    """
    username = message.username[:20].ljust(20, '\0')  
    text = message.text[:140].ljust(141, '\0')  

    text_size = len(text.encode('utf-8'))

    message = struct.pack('!IIII20s141s', message.message_type, message.origin_id, message.destination_id, text_size, username.encode('utf-8'), text.encode('utf-8'))

    return message


def decode_message(message: bytes) -> TwotterMessage:
    """
    Decodes a bytes object into a TwotterMessage object.
    """
    msg_type, origin_id, destination_id, text_size, username, text = struct.unpack('!IIII20s141s', message)
    
    username = username.decode('utf-8').strip('\0')
    text = text.decode('utf-8').strip('\0')
    
    return TwotterMessage(msg_type, 
                          origin_id, 
                          destination_id, 
                          username, 
                          text)
