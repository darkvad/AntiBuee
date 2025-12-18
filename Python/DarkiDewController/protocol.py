import struct
from enum import IntEnum
from datetime import datetime
import logging

class Command(IntEnum):
    """Commandes du protocole"""
    HELLO = 0x30
    DELTA = 0x31
    OFFSET = 0x32
    ALREADY_CONNECTED = 0x33
    ERROR = 0x34
    RECEIVED = 0x35
    FULL = 0x36
    REGUL = 0x37
    STATUS = 0x38

class ProtocolHandler:
    """Gestionnaire du protocole binaire"""
    
    def __init__(self):
        self.connection_status = None
        self.last_command = None
        self.response_buffer = bytearray()
        self.in_status_response = False
        self.status_buffer = ""
        self.logger = logging.getLogger(__name__)
        self.buffer = bytearray()
    
    def create_hello_command(self):
        """Crée la commande HELLO (0x30)"""
        return bytes([Command.HELLO])
    
    def create_delta_command(self, value):
        """
        Crée la commande SET DELTA TEMP (0x31)
        value: 0-9 (converti en 0x30-0x39)
        """
        if 0 <= value <= 9:
            value_byte = 0x30 + value  # Convertit 0->0x30, 1->0x31, etc.
            return bytes([Command.DELTA, value_byte])
        else:
            raise ValueError(f"Valeur delta invalide: {value}. Doit être entre 0 et 9")
    
    def create_offset_command(self, value):
        """
        Crée la commande SET OFFSET (0x32)
        value: 0-9 (converti en 0x30-0x39)
        """
        if 0 <= value <= 9:
            value_byte = 0x30 + value
            return bytes([Command.OFFSET, value_byte])
        else:
            raise ValueError(f"Valeur offset invalide: {value}. Doit être entre 0 et 9")
    
    def create_mode_command(self, is_maxi=True, value=100):
        """Crée la commande SET MODE"""
        if is_maxi:
            if 0 <= value <= 100:
                value_byte = ((255 * value) // 100)
                return bytes([Command.FULL, value_byte])
            else:
                raise ValueError(f"Valeur puissance invalide: {value}. Doit être entre 0 et 100")
            #return bytes([Command.FULL])
        else:
            return bytes([Command.REGUL])
    
    def create_status_command(self):
        """Crée la commande STATUS (0x38)"""
        return bytes([Command.STATUS])
    
    def feed(self, data):
        """Ajoute des données au buffer et retourne une liste de trames complètes."""
        self.buffer.extend(data)
        frames = []
        while True:
            frame = self._extract_frame()
            if frame is None:
                break
            frames.append(frame)
        return frames
    
    def _extract_frame(self):
        """Extrait une trame du buffer si une trame complète est disponible."""
        # Cherche la séquence de fin de trame pour STATUS
        idx = self.buffer.find(b']\x35')
        if idx != -1:
            frame = self.buffer[:idx+2]
            self.buffer = self.buffer[idx+2:]
            self.logger.debug(f"Extracted STATUS frame: {frame.hex()}")
            return frame
        
        # Cherche un acquittement simple (0x35 ou 0x34)
        for i, byte in enumerate(self.buffer):
            if byte in (0x35, 0x34):
                frame = self.buffer[:i+1]
                self.buffer = self.buffer[i+1:]
                self.logger.debug(f"Extracted ACK/ERROR frame: {frame.hex()}")
                return frame
        
        # Aucune trame complète trouvée
        return None
    
    def parse_response(self, frame):
        """
        Parse une trame complète.
        Retourne (commande, données_parsées)
        """
        self.logger.debug(f"Parsing frame: {frame.hex()}")
        
        # Acquittement simple
        if frame == bytes([Command.RECEIVED]):
            return Command.RECEIVED, {'ack': True}
        
        # Erreur simple
        if frame == bytes([Command.ERROR]):
            return Command.ERROR, {'ack': False, 'error': True}
        
        # Réponse HELLO (0x30 0x05 ou 0x33 0x05)
        if len(frame) == 2 and frame[0] in (Command.HELLO, Command.ALREADY_CONNECTED) and frame[1] == 0x05:
            return Command.HELLO, {'first_connection': (frame[0] == Command.HELLO)}
        
        # Réponse STATUS
        if frame.startswith(b'[') and frame.endswith(b']\x35'):
            # Extraire la chaîne entre crochets
            status_str = frame[1:-2].decode('ascii', errors='ignore')
            parsed = self._parse_status_response('[' + status_str + ']')
            return Command.STATUS, parsed
        
        # Si on arrive ici, on ne sait pas parser
        self.logger.warning(f"Unknown frame: {frame.hex()}")
        return None, {'raw': frame}
    
    def _parse_status_response(self, status_str):
        """Parse la chaîne de statut."""
        try:
            if status_str.startswith('[') and status_str.endswith(']'):
                content = status_str[1:-1]
            else:
                content = status_str
            
            parts = content.split('#')
            if len(parts) == 7:
                return {
                    'temperature': float(parts[0]),
                    'humidity': float(parts[1]),
                    'tube_temperature': float(parts[2]),
                    'dew_point': float(parts[3]),
                    'pwm': float(parts[4]),
                    'delta_temp': int(parts[5]),
                    'dew_offset': int(parts[6]),
                    'timestamp': datetime.now()
                }
            else:
                self.logger.warning(f"Invalid STATUS format: {status_str}")
                return {'raw': status_str, 'error': 'Invalid format'}
        except Exception as e:
            self.logger.error(f"Error parsing STATUS: {e}")
            return {'raw': status_str, 'error': str(e)}
            
    def set_last_command(self, command):
        """Enregistre la dernière commande envoyée"""
        self.last_command = command
    
    def reset(self):
        """Réinitialise l'état du protocole"""
        self.in_status_response = False
        self.status_buffer = ""
        self.last_command = None
    
    def validate_delta_value(self, value):
        """Valide la valeur delta (0-9)"""
        return 0 <= value <= 9
    
    def validate_offset_value(self, value):
        """Valide la valeur offset (0-9)"""
        return 0 <= value <= 9