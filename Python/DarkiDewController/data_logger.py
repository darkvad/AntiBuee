import csv
import json
import logging
from datetime import datetime
import os
from pathlib import Path

class DataLogger:
    """Système de journalisation des données"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.session_id = None
        self.csv_writer = None
        self.csv_file = None
        self.json_file = None
        self.setup_logging()
        
    def setup_logging(self):
        """Configure le système de logging"""
        # Créer le répertoire de logs s'il n'existe pas
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurer le logging Python
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / 'application.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def start_new_session(self):
        """Démarre une nouvelle session de logging"""
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Créer les fichiers de log
        try:
            # Fichier CSV pour les données structurées
            csv_path = self.log_dir / f"data_{self.session_id}.csv"
            self.csv_file = open(csv_path, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            
            # En-tête CSV
            header = [
                'timestamp', 'temperature', 'humidity', 'tube_temperature',
                'dew_point', 'pwm', 'delta_temp', 'dew_offset'
            ]
            self.csv_writer.writerow(header)
            
            # Fichier JSON pour les données brutes et événements
            json_path = self.log_dir / f"events_{self.session_id}.jsonl"
            self.json_file = open(json_path, 'w')
            
            self.logger.info(f"Nouvelle session démarrée: {self.session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur démarrage session: {e}")
            return False
    
    def log_parsed_data(self, data):
        """Journalise les données parsées"""
        if not self.csv_writer:
            return
        
        try:
            row = [
                data.get('timestamp', datetime.now()).isoformat(),
                data.get('temperature', ''),
                data.get('humidity', ''),
                data.get('tube_temperature', ''),
                data.get('dew_point', ''),
                data.get('pwm', ''),
                data.get('delta_temp', ''),
                data.get('dew_offset', '')
            ]
            self.csv_writer.writerow(row)
            self.csv_file.flush()
            
            # Également log en JSON
            self._log_json('DATA', data)
            
        except Exception as e:
            self.logger.error(f"Erreur journalisation données: {e}")
    
    def log_raw_data(self, data, direction="RX"):
        """Journalise les données brutes"""
        try:
            event = {
                'type': 'RAW',
                'direction': direction,
                'timestamp': datetime.now().isoformat(),
                'data_hex': data.hex() if isinstance(data, bytes) else str(data),
                'data_length': len(data)
            }
            self._log_json('RAW', event)
        except Exception as e:
            self.logger.error(f"Erreur journalisation raw: {e}")
    
    def log_event(self, event_type, message):
        """Journalise un événement"""
        try:
            event = {
                'type': event_type,
                'timestamp': datetime.now().isoformat(),
                'message': message
            }
            self._log_json('EVENT', event)
            self.logger.info(f"{event_type}: {message}")
        except Exception as e:
            self.logger.error(f"Erreur journalisation événement: {e}")
    
    def _log_json(self, event_type, data):
        """Log un événement au format JSONL"""
        if not self.json_file:
            return
        
        try:
            log_entry = {
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            self.json_file.write(json.dumps(log_entry) + '\n')
            self.json_file.flush()
        except Exception as e:
            self.logger.error(f"Erreur écriture JSON: {e}")
    
    def get_log_files(self):
        """Retourne la liste des fichiers de log"""
        try:
            return [f.name for f in self.log_dir.glob("*") if f.is_file()]
        except Exception as e:
            self.logger.error(f"Erreur liste fichiers log: {e}")
            return []
    
    def export_logs(self, directory):
        """Exporte les logs vers un autre répertoire"""
        try:
            dest_dir = Path(directory)
            dest_dir.mkdir(exist_ok=True)
            
            for log_file in self.log_dir.glob("*"):
                if log_file.is_file():
                    dest_file = dest_dir / log_file.name
                    log_file.rename(dest_file)
            
            self.logger.info(f"Logs exportés vers {directory}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur export logs: {e}")
            return False
    
    def stop_logging(self):
        """Arrête la journalisation et ferme les fichiers"""
        try:
            if self.csv_file:
                self.csv_file.close()
            if self.json_file:
                self.json_file.close()
            
            self.csv_writer = None
            self.csv_file = None
            self.json_file = None
            
            self.logger.info("Journalisation arrêtée")
        except Exception as e:
            self.logger.error(f"Erreur arrêt journalisation: {e}")
    
    def __del__(self):
        """Destructeur pour fermer les fichiers"""
        self.stop_logging()