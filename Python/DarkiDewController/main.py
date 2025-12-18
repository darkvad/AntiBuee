import sys
import os
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import pyqtgraph as pg
import numpy as np
from datetime import datetime, timedelta
import threading
import time
import csv
import json
from collections import deque
import logging

# Imports locaux
from protocol import ProtocolHandler, Command
from data_logger import DataLogger
from realtime_plots import RealTimePlot, MultiPlotWidget

class SerialWorker(QObject):
    """Version corrigée avec tous les signaux nécessaires"""
    
    # Tous les signaux requis
    data_received = pyqtSignal(dict)
    status_update = pyqtSignal(str)
    command_ack = pyqtSignal(str, bool)
    raw_data_received = pyqtSignal(bytes)  # Ajouté ici !
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.running = False
        self.baudrate = 19200
        self.protocol = ProtocolHandler()
        self.data_logger = DataLogger()
        
        # États améliorés
        self.awaiting_response = False
        self.current_command = None
        self.response_buffer = bytearray()
        self.status_parsing_state = "WAITING_START"  # WAITING_START, IN_DATA, WAITING_ACK
        
        # Timeout
        self.command_start_time = None
        self.timeout_duration = 10  # 10 secondes par défaut
        
        self.setup_logging()
    
    def setup_logging(self):
        import logging
        self.logger = logging.getLogger('SerialWorker')
        self.logger.setLevel(logging.DEBUG)
        
        handler = logging.FileHandler('serial_corrected.log', mode='w')
        handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d - STATE:%(state)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self.logger.info("SerialWorker corrigé initialisé", extra={'state': 'INIT'})
    
    def _log_with_state(self, message, level=logging.INFO):
        """Log avec l'état courant"""
        self.logger.log(level, message, extra={'state': self.status_parsing_state})
    
    def connect(self, port, baudrate=19200):
        """Connexion simple"""
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=0.1,
                write_timeout=2.0
            )
            self.baudrate = baudrate
            self.running = True
            
            # Démarrer la lecture
            self.read_thread = threading.Thread(target=self.read_data, daemon=True)
            self.read_thread.start()
            
            # Attendre le démarrage puis envoyer HELLO
            threading.Thread(target=self._delayed_startup, daemon=True).start()
            
            self.status_update.emit(f"Connecté à {port}. Attente démarrage...")
            return True
            
        except Exception as e:
            self._log_with_state(f"Erreur connexion: {e}", logging.ERROR)
            self.status_update.emit(f"Erreur: {e}")
            return False
    
    def _delayed_startup(self):
        """Procédure de démarrage avec délai"""
        time.sleep(10)  # Attendre le démarrage du périphérique
        if self.running:
            self._log_with_state("Envoi HELLO après démarrage")
            self.send_hello()
            time.sleep(5.0)
            self._log_with_state("Envoi STATUS après démarrage")
            self.request_status()
    
    def send_hello(self):
        """Envoie HELLO"""
        self._send_command(b'\x30', "HELLO")
    
    def send_delta_temp(self, value):
        """Envoie SET DELTA TEMP"""
        try:
            cmd = self.protocol.create_delta_command(value)
            return self._send_command(cmd, "DELTA")
        except ValueError as e:
            self._log_with_state(f"Erreur DELTA: {e}", logging.ERROR)
            return False
    
    def send_dew_offset(self, value):
        """Envoie SET OFFSET"""
        try:
            cmd = self.protocol.create_offset_command(value)
            return self._send_command(cmd, "OFFSET")
        except ValueError as e:
            self._log_with_state(f"Erreur OFFSET: {e}", logging.ERROR)
            return False
    
    def send_mode(self, is_maxi=True, value=255):
        """Envoie SET MODE"""
        cmd = self.protocol.create_mode_command(is_maxi, value)
        cmd_name = "FULL" if is_maxi else "REGUL"
        self._send_command(cmd, cmd_name)
    
    def request_status(self):
        """Envoie STATUS avec parsing d'état"""
        self._send_command(b'\x38', "STATUS")

    def send_save(self):
        """Envoie SAVE avec parsing d'état"""
        self._send_command(b'\x39', "SAVE")

    def _send_command(self, cmd_bytes, cmd_name):
        """Envoie une commande"""
        if not self.serial_port or not self.serial_port.is_open:
            self._log_with_state("Port série non ouvert", logging.ERROR)
            return False
        
        # Si une commande est en cours, attendre
        if self.awaiting_response:
            self._log_with_state(f"Impossible d'envoyer {cmd_name}: commande en cours", logging.WARNING)
            return False
        
        try:
            # Petit délai avant envoi
            time.sleep(0.1)
            
            # Réinitialiser l'état de parsing
            self.status_parsing_state = "WAITING_START" if cmd_name == "STATUS" else "IDLE"
            self.response_buffer.clear()
            
            # Envoyer la commande
            self._log_with_state(f"Envoi {cmd_name}: {cmd_bytes.hex()}")
            self.serial_port.write(cmd_bytes)
            self.serial_port.flush()
            
            # Configurer l'attente
            self.awaiting_response = True
            self.current_command = cmd_name
            self.command_start_time = time.time()
            
            self.status_update.emit(f"{cmd_name} envoyé")
            self.data_logger.log_raw_data(cmd_bytes, direction="TX")
            
            return True
            
        except Exception as e:
            error_msg = f"Erreur envoi {cmd_name}: {str(e)}"
            self._log_with_state(error_msg, logging.ERROR)
            self.status_update.emit(error_msg)
            return False
    
    def read_data(self):
        """Lecture des données avec machine à états"""
        self._log_with_state("Démarrage lecture")
        
        while self.running and self.serial_port and self.serial_port.is_open:
            try:
                # Lire les données disponibles
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    
                    if data:
                        self._log_with_state(f"Reçu {len(data)} octets: {data.hex()[:50]}...")
                        self.data_logger.log_raw_data(data, direction="RX")
                        
                        # Émettre les données brutes pour la console
                        self.raw_data_received.emit(data)  # <-- CORRECTION ICI
                        
                        # Traiter selon la commande en cours
                        if self.awaiting_response:
                            self.response_buffer.extend(data)
                            self._process_received_data()
                
                # Vérifier le timeout
                self._check_timeout()
                
                time.sleep(0.01)
                
            except Exception as e:
                self._log_with_state(f"Erreur lecture: {e}", logging.ERROR)
                time.sleep(1)
        
        self._log_with_state("Arrêt lecture")
    
    def _check_timeout(self):
        """Vérifie si la commande courante a expiré"""
        if self.awaiting_response and self.command_start_time:
            elapsed = time.time() - self.command_start_time
            
            # Timeout plus long pour STATUS (15 secondes)
            timeout = 15 if self.current_command == "STATUS" else 5
            
            if elapsed > timeout:
                self._log_with_state(f"Timeout {self.current_command} ({elapsed:.1f}s)", logging.ERROR)
                self.status_update.emit(f"Timeout {self.current_command}")
                self.command_ack.emit(self.current_command, False)
                
                # Réinitialiser
                self._reset_state()
    
    def _reset_state(self):
        """Réinitialise l'état du worker"""
        self.awaiting_response = False
        self.current_command = None
        self.status_parsing_state = "IDLE"
        self.response_buffer.clear()
        self.command_start_time = None
    
    def _process_received_data(self):
        """Traite les données reçues selon la commande"""
        if not self.awaiting_response:
            return
        
        self._log_with_state(f"Buffer: {self.response_buffer.hex()[:100]}...")
        
        if self.current_command == "STATUS":
            self._process_status_response_smart()
        elif self.current_command == "HELLO":
            self._process_hello_response()
        else:  # DELTA, OFFSET, FULL, REGUL, SAVE
            self._process_simple_response()
    
    def _process_status_response_smart(self):
        """
        Traite la réponse STATUS intelligemment
        - Ne cherche pas 0x34 dans les données
        - Cherche seulement [données] + 0x35 à la fin
        """
        try:
            # Convertir en string pour analyse
            buffer_str = ""
            for byte in self.response_buffer:
                if 32 <= byte <= 126:  # Caractères ASCII imprimables
                    buffer_str += chr(byte)
                elif byte == 0x5B:  # '['
                    buffer_str += '['
                elif byte == 0x5D:  # ']'
                    buffer_str += ']'
                elif byte == 0x23:  # '#'
                    buffer_str += '#'
                else:
                    buffer_str += f"\\x{byte:02X}"
            
            self._log_with_state(f"Buffer ASCII: {buffer_str[:100]}...")
            
            # État 1: Attente du début '['
            if self.status_parsing_state == "WAITING_START":
                if '[' in buffer_str:
                    self._log_with_state("Début '[' détecté")
                    self.status_parsing_state = "IN_DATA"
                else:
                    # Pas encore de début, continuer d'attendre
                    return
            
            # État 2: Dans les données, attendre la fin ']'
            if self.status_parsing_state == "IN_DATA":
                if ']' in buffer_str:
                    # Trouver la position du ']' dans le buffer d'octets
                    # Nous devons trouver le byte 0x5D dans self.response_buffer
                    for i, byte in enumerate(self.response_buffer):
                        if byte == 0x5D:  # ']'
                            self._log_with_state(f"Fin ']' détectée à la position {i}")
                            
                            # Vérifier si on a le byte suivant pour l'ACK
                            if len(self.response_buffer) > i + 1:
                                next_byte = self.response_buffer[i + 1]
                                
                                if next_byte == 0x35:  # ACK
                                    self._log_with_state("ACK 0x35 détecté après ']'")
                                    self._parse_and_emit_status(i)
                                    self.command_ack.emit("STATUS", True)
                                    self._reset_state()
                                    return
                                elif next_byte == 0x34:  # NAK
                                    # C'est un vrai NAK, pas un chiffre 4
                                    self._log_with_state("NAK 0x34 détecté après ']'", logging.ERROR)
                                    self.command_ack.emit("STATUS", False)
                                    self._reset_state()
                                    return
                                else:
                                    self._log_with_state(f"Byte inattendu après ']': 0x{next_byte:02X}", logging.WARNING)
                                    # Attendre plus de données
                                    return
                            else:
                                # On a le ']' mais pas encore l'ACK, attendre
                                self.status_parsing_state = "WAITING_ACK"
                                return
                    # Si on arrive ici, on a trouvé ']' dans la string mais pas dans les bytes? Impossible
                    return
            
            # État 3: On a le ']', on attend l'ACK
            if self.status_parsing_state == "WAITING_ACK":
                # Trouver le dernier ']' dans le buffer
                for i, byte in enumerate(self.response_buffer):
                    if byte == 0x5D:  # ']'
                        last_bracket_pos = i
                
                if last_bracket_pos is not None and len(self.response_buffer) > last_bracket_pos + 1:
                    next_byte = self.response_buffer[last_bracket_pos + 1]
                    
                    if next_byte == 0x35:
                        self._log_with_state("ACK 0x35 reçu après attente")
                        self._parse_and_emit_status(last_bracket_pos)
                        self.command_ack.emit("STATUS", True)
                        self._reset_state()
                    elif next_byte == 0x34:
                        self._log_with_state("NAK 0x34 reçu après attente", logging.ERROR)
                        self.command_ack.emit("STATUS", False)
                        self._reset_state()
                    # Sinon, continuer d'attendre
            
        except Exception as e:
            self._log_with_state(f"Erreur traitement STATUS: {e}", logging.ERROR)
            self._reset_state()
    
    def _parse_and_emit_status(self, bracket_pos):
        """Parse et émet les données STATUS"""
        try:
            # Extraire les données jusqu'au ']'
            # On sait que le buffer commence par '[' (0x5B)
            if self.response_buffer[0] != 0x5B:
                self._log_with_state("Buffer STATUS ne commence pas par '['", logging.ERROR)
                return
            
            # Extraire les données entre '[' et ']'
            data_bytes = self.response_buffer[1:bracket_pos]  # Exclure le ']'
            data_str = data_bytes.decode('ascii', errors='ignore')
            
            self._log_with_state(f"Données STATUS brutes: {data_str}")
            
            # Parser selon le format: valeur#valeur#...
            parts = data_str.split('#')
            if len(parts) == 7:
                parsed = {
                    'temperature': float(parts[0]),
                    'humidity': float(parts[1]),
                    'tube_temperature': float(parts[2]),
                    'dew_point': float(parts[3]),
                    'pwm': float(parts[4]),
                    'delta_temp': int(parts[5]),
                    'dew_offset': int(parts[6])
                }
                self.data_received.emit(parsed)
                self._log_with_state(f"STATUS parsé: {parsed}")
            else:
                self._log_with_state(f"Format STATUS invalide: {len(parts)} parties au lieu de 7", logging.ERROR)
                
        except Exception as e:
            self._log_with_state(f"Erreur parsing STATUS: {e}", logging.ERROR)
    
    def _process_hello_response(self):
        """Traite la réponse HELLO"""
        try:
            # Format attendu: 0x30 0x35 ou 0x33 0x35
            if len(self.response_buffer) >= 2:
                if self.response_buffer[0] == 0x30 and self.response_buffer[1] == 0x35:
                    self._log_with_state("HELLO: Première connexion")
                    self.status_update.emit("Première connexion établie")
                    self.command_ack.emit("HELLO", True)
                    self._reset_state()
                elif self.response_buffer[0] == 0x33 and self.response_buffer[1] == 0x35:
                    self._log_with_state("HELLO: Déjà connecté")
                    self.status_update.emit("Déjà connecté")
                    self.command_ack.emit("HELLO", True)
                    self._reset_state()
            
            # Erreur 0x34 (attention: seul, pas dans des données)
            elif len(self.response_buffer) >= 1 and self.response_buffer[0] == 0x34:
                self._log_with_state("HELLO: Erreur 0x34", logging.ERROR)
                self.command_ack.emit("HELLO", False)
                self._reset_state()
                
        except Exception as e:
            self._log_with_state(f"Erreur traitement HELLO: {e}", logging.ERROR)
            self._reset_state()
    
    def _process_simple_response(self):
        """Traite les réponses simples (DELTA, OFFSET, MODE)"""
        try:
            # Ces commandes renvoient juste 0x35 (ACK) ou 0x34 (NAK)
            # On peut les chercher car il n'y a pas de données
            if 0x35 in self.response_buffer:
                self._log_with_state(f"{self.current_command}: ACK reçu")
                self.command_ack.emit(self.current_command, True)
                self._reset_state()
            elif 0x34 in self.response_buffer:
                self._log_with_state(f"{self.current_command}: NAK reçu", logging.ERROR)
                self.command_ack.emit(self.current_command, False)
                self._reset_state()
                
        except Exception as e:
            self._log_with_state(f"Erreur traitement {self.current_command}: {e}", logging.ERROR)
            self._reset_state()
    
    def disconnect(self):
        """Déconnexion"""
        self._log_with_state("Déconnexion")
        self.running = False
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        
        self.status_update.emit("Déconnecté")
        
    def _attempt_reconnect(self):
        """Tente de se reconnecter"""
        if self.serial_port and self.serial_port.port:
            port = self.serial_port.port
            self.disconnect()
            time.sleep(1)
            return self.connect(port, self.baudrate)
        return False
    
    def get_log_files(self):
        """Retourne la liste des fichiers de log"""
        return self.data_logger.get_log_files()
    
    def export_logs(self, directory):
        """Exporte les logs vers un répertoire"""
        return self.data_logger.export_logs(directory)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contrôleur de Buée avec Anneau Chauffant - Protocole Binaire")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialisation des données
        self.plot_data = {
            'temperature': deque(maxlen=1000),
            'humidity': deque(maxlen=1000),
            'tube_temperature': deque(maxlen=1000),
            'dew_point': deque(maxlen=1000),
            'pwm': deque(maxlen=1000),
            'delta_temp': deque(maxlen=1000),
            'dew_offset': deque(maxlen=1000)
        }
        self.timestamps = deque(maxlen=1000)
        
        # Initialiser le worker série
        self.serial_worker = SerialWorker()
        self.worker_thread = QThread()
        
        # Configuration de l'interface
        self.init_ui()
        self.init_serial_thread()
        self.refresh_ports()
        
        # Timer pour les mises à jour automatiques
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.auto_request_status)
        self.status_timer.start(5000)  # Toutes les 5 secondes
        
        # Configuration du logging
        self.setup_logging()
        # Ajouter un indicateur de statut de connexion
        self.connection_status = QLabel("Non connecté")
        self.connection_status.setStyleSheet("""
            QLabel {
                padding: 5px;
                border-radius: 3px;
                font-weight: bold;
            }
            QLabel[status="disconnected"] {
                background-color: #f44336;
                color: white;
            }
            QLabel[status="connecting"] {
                background-color: #ff9800;
                color: white;
            }
            QLabel[status="connected"] {
                background-color: #4CAF50;
                color: white;
            }
        """)
        self.connection_status.setProperty("status", "disconnected")
        
        # Ajouter à la barre de statut
        #self.status_bar.addWidget(self.connection_status)
        
        # Timer pour les requêtes automatiques
        self.auto_status_timer = QTimer()
        self.auto_status_timer.timeout.connect(self.auto_request_status)
        
        # Configuration des délais
        self.device_boot_time = 12  # secondes
        self.command_delay = 5      # secondes
        
    def toggle_connection(self):
        """Connecte/Déconnecte avec gestion des délais"""
        if self.serial_worker.serial_port and self.serial_worker.serial_port.is_open:
            # Déconnexion
            self.serial_worker.disconnect()
            self.connect_btn.setText("Connecter")
            self.connection_status.setText("Non connecté")
            self.connection_status.setProperty("status", "disconnected")
            self.connection_status.style().polish(self.connection_status)
            self.auto_status_timer.stop()
            
        else:
            # Connexion
            port = self.port_combo.currentData()
            baudrate = int(self.baudrate_combo.currentText())
            
            if port:
                self.connection_status.setText("Connexion...")
                self.connection_status.setProperty("status", "connecting")
                self.connection_status.style().polish(self.connection_status)
                self.connect_btn.setEnabled(False)
                
                # Connexion dans un thread séparé pour ne pas bloquer l'UI
                QTimer.singleShot(100, lambda: self._perform_connection(port, baudrate))
    
    def _perform_connection(self, port, baudrate):
        """Effectue la connexion dans un thread séparé"""
        if self.serial_worker.connect(port, baudrate):
            self.connect_btn.setText("Déconnecter")
            self.connection_status.setText("Attente démarrage périphérique (10s)...")
            self.connection_status.setProperty("status", "connected")
            
            # Réactiver le bouton
            self.connect_btn.setEnabled(True)
            
            # Démarrer le timer pour vérifier quand le périphérique est prêt
            QTimer.singleShot(11000, self._check_device_ready)  # 11s pour être sûr
        else:
            self.connect_btn.setEnabled(True)
            self.connection_status.setText("Échec connexion")
            self.connection_status.setProperty("status", "disconnected")
    
    def _check_device_ready(self):
        """Vérifie si le périphérique est prêt après le démarrage"""
        if self.serial_worker.is_device_ready:
            self.connection_status.setText("Connecté")
            self.connection_status.setProperty("status", "connected")
            self.connection_status.style().polish(self.connection_status)
            
            # Démarrer les requêtes automatiques de STATUS
            self.auto_status_timer.start(10000)  # Toutes les 10 secondes
        else:
            # Réessayer dans 1 seconde
            QTimer.singleShot(1000, self._check_device_ready)
    
    def update_status_bar(self, message):
        """Met à jour la barre de statut avec indication de temporisation"""
        # Afficher le message
        self.status_bar.showMessage(message, 5000)
        
        # Si c'est un message d'attente, l'afficher dans l'indicateur de connexion
        if "Attente" in message or "waiting" in message.lower():
            self.connection_status.setText(message[:30] + "...")
    
    def send_variables(self):
        """Envoie les variables avec gestion du délai"""
        if not self.serial_worker.is_device_ready:
            QMessageBox.warning(self, "Périphérique non prêt", 
                              "Veuillez attendre que le périphérique soit prêt")
            return
        
        # Désactiver le bouton pendant l'envoi
        self.send_vars_btn.setEnabled(False)
        self.send_vars_btn.setText("Envoi...")
        
        # Récupérer les valeurs
        delta = self.delta_spin.value()
        offset = self.offset_spin.value()
        
        # Envoyer dans un thread séparé
        def send_commands():
            # Envoyer DELTA
            success1 = self.serial_worker.send_delta_temp(delta)
            time.sleep(0.5)  # Petit délai entre les commandes
            
            # Envoyer OFFSET
            success2 = self.serial_worker.send_dew_offset(offset)
            
            # Réactiver le bouton
            QTimer.singleShot(0, lambda: self._on_commands_sent(success1 and success2))
        
        threading.Thread(target=send_commands, daemon=True).start()
    
    def _on_commands_sent(self, success):
        """Callback après envoi des commandes"""
        self.send_vars_btn.setEnabled(True)
        self.send_vars_btn.setText("Envoyer Variables")
        
        if success:
            self.status_bar.showMessage("Commandes envoyées avec succès", 3000)
        else:
            self.status_bar.showMessage("Erreur lors de l'envoi des commandes", 3000)
    
    def auto_request_status(self):
        """Requête automatique de STATUS avec vérification"""
        if (self.serial_worker.serial_port and 
            self.serial_worker.serial_port.is_open and
            self.serial_worker.is_device_ready and
            self.auto_status_check.isChecked()):
            
            # Vérifier qu'aucune autre commande n'est en cours
            if not self.serial_worker.awaiting_response:
                self.serial_worker.request_status()
            else:
                self.logger.debug("STATUS automatique reporté: commande en cours")
    
    def setup_logging(self):
        """Configure le système de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('app.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def init_serial_thread(self):
        """Initialise le thread pour la communication série"""
        self.serial_worker.moveToThread(self.worker_thread)
        
        # Connexion des signaux
        self.serial_worker.data_received.connect(self.update_display)
        self.serial_worker.status_update.connect(self.update_status_bar)
        self.serial_worker.raw_data_received.connect(self.update_raw_console)
        self.serial_worker.command_ack.connect(self.handle_command_ack)
        
        self.worker_thread.start()
        
        # Démarrer la lecture dans le thread
        QTimer.singleShot(100, self.serial_worker.read_data)
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        # Créer un widget central avec onglets
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Onglet 1: Contrôle principal
        self.create_control_tab()
        
        # Onglet 2: Graphiques
        self.create_plots_tab()
        
        # Onglet 3: Journalisation
        self.create_logging_tab()
        
        # Onglet 4: Configuration
        self.create_config_tab()
    
        # Onglet 5: Diagnostics
        self.create_diagnostic_tab()
        
        # Barre de statut
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Prêt")
        self.status_bar.addPermanentWidget(self.status_label)
    
    def create_control_tab(self):
        """Crée l'onglet de contrôle principal"""
        control_tab = QWidget()
        layout = QVBoxLayout(control_tab)
        
        # Section connexion série
        connection_group = QGroupBox("Connexion Série")
        connection_layout = QGridLayout()
        
        # Port série
        connection_layout.addWidget(QLabel("Port:"), 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(200)
        connection_layout.addWidget(self.port_combo, 0, 1)
        
        # Baudrate
        connection_layout.addWidget(QLabel("Baudrate:"), 0, 2)
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baudrate_combo.setCurrentText("19200")
        connection_layout.addWidget(self.baudrate_combo, 0, 3)
        
        # Boutons
        refresh_btn = QPushButton("Rafraîchir")
        refresh_btn.clicked.connect(self.refresh_ports)
        connection_layout.addWidget(refresh_btn, 0, 4)
        
        self.connect_btn = QPushButton("Connecter")
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.connect_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        connection_layout.addWidget(self.connect_btn, 0, 5)
        
        connection_group.setLayout(connection_layout)
        
        # Section commandes
        commands_group = QGroupBox("Commandes")
        commands_layout = QGridLayout()
        
        # HELLO
        hello_btn = QPushButton("HELLO (0x30)")
        hello_btn.clicked.connect(lambda: self.serial_worker.send_hello())
        commands_layout.addWidget(hello_btn, 0, 0)
        
        # SAVE
        eeprom_btn = QPushButton("SAVE EEPROM (0x39)")
        eeprom_btn.clicked.connect(lambda: self.serial_worker.send_save())
        commands_layout.addWidget(eeprom_btn, 0, 2)
        
        # Delta Temp
        commands_layout.addWidget(QLabel("Delta Temp (0-9):"), 1, 0)
        self.delta_spin = QSpinBox()
        self.delta_spin.setRange(0, 9)
        self.delta_spin.setValue(0)
        commands_layout.addWidget(self.delta_spin, 1, 1)
        
        delta_btn = QPushButton("SET DELTA (0x31)")
        delta_btn.clicked.connect(lambda: self.serial_worker.send_delta_temp(self.delta_spin.value()))
        commands_layout.addWidget(delta_btn, 1, 2)
        
        # Offset Rosée
        commands_layout.addWidget(QLabel("Offset Rosée (0-9):"), 2, 0)
        self.offset_spin = QSpinBox()
        self.offset_spin.setRange(0, 9)
        self.offset_spin.setValue(0)
        commands_layout.addWidget(self.offset_spin, 2, 1)
        
        offset_btn = QPushButton("SET OFFSET (0x32)")
        offset_btn.clicked.connect(lambda: self.serial_worker.send_dew_offset(self.offset_spin.value()))
        commands_layout.addWidget(offset_btn, 2, 2)
        
        # Mode
        commands_layout.addWidget(QLabel("Mode:"), 3, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Régulation (0x37)", "Maxi (0x36)"])
        commands_layout.addWidget(self.mode_combo, 3, 1)
        
        mode_btn = QPushButton("SET MODE")
        mode_btn.clicked.connect(self.send_mode_command)
        commands_layout.addWidget(mode_btn, 3, 2)
        
        # PWM Fixe
        commands_layout.addWidget(QLabel("Puissance pour mode maxi (0-100 %):"), 4, 0)
        self.power_spin = QSpinBox()
        self.power_spin.setRange(0, 100)
        self.power_spin.setValue(100)
        commands_layout.addWidget(self.power_spin, 4, 1)
         
        # STATUS
        status_btn = QPushButton("STATUS (0x38)")
        status_btn.clicked.connect(lambda: self.serial_worker.request_status())
        status_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        commands_layout.addWidget(status_btn, 5, 0, 1, 3)
        
        commands_group.setLayout(commands_layout)
        
        # Section affichage statut
        status_group = QGroupBox("Statut Actuel")
        status_layout = QGridLayout()
        
        # Créer des labels pour chaque valeur
        self.status_labels = {}
        status_fields = [
            ("Température", "temperature", "°C"),
            ("Humidité", "humidity", "%"),
            ("Temp Tube", "tube_temperature", "°C"),
            ("Point de Rosée", "dew_point", "°C"),
            ("PWM", "pwm", ""),
            ("Delta Temp", "delta_temp", ""),
            ("Offset Rosée", "dew_offset", "")
        ]
        
        for i, (label, key, unit) in enumerate(status_fields):
            status_layout.addWidget(QLabel(f"{label}:"), i, 0)
            value_label = QLabel("--")
            value_label.setStyleSheet("font: 12pt; padding: 2px;")
            value_label.setMinimumWidth(80)
            self.status_labels[key] = value_label
            status_layout.addWidget(value_label, i, 1)
            status_layout.addWidget(QLabel(unit), i, 2)
        
        status_group.setLayout(status_layout)
        
        # Console HEX
        console_group = QGroupBox("Console HEX")
        console_layout = QVBoxLayout()
        
        self.hex_console = QTextEdit()
        self.hex_console.setReadOnly(True)
        self.hex_console.setMaximumHeight(150)
        self.hex_console.setFont(QFont("Courier", 9))
        
        console_layout.addWidget(self.hex_console)
        console_group.setLayout(console_layout)
        
        # Assemblage
        layout.addWidget(connection_group)
        layout.addWidget(commands_group)
        layout.addWidget(status_group)
        layout.addWidget(console_group)
        
        self.tab_widget.addTab(control_tab, "Contrôle")
    
    def create_plots_tab(self):
        """Crée l'onglet des graphiques"""
        plots_tab = QWidget()
        layout = QVBoxLayout(plots_tab)
        
        # Widget avec plusieurs graphiques
        self.multi_plot = MultiPlotWidget()
        layout.addWidget(self.multi_plot)
        
        # Contrôles des graphiques
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        
        # Intervalle de mise à jour
        controls_layout.addWidget(QLabel("Intervalle STATUS:"))
        self.update_interval = QSpinBox()
        self.update_interval.setRange(1, 120)
        self.update_interval.setValue(120)
        self.update_interval.setSuffix(" s")
        self.update_interval.valueChanged.connect(self.update_status_interval)
        controls_layout.addWidget(self.update_interval)
        
        # Bouton pause
        self.pause_plots_btn = QPushButton("Pause Graphiques")
        self.pause_plots_btn.setCheckable(True)
        self.pause_plots_btn.toggled.connect(self.toggle_plots_pause)
        controls_layout.addWidget(self.pause_plots_btn)
        
        # Bouton effacer
        clear_btn = QPushButton("Effacer Graphiques")
        clear_btn.clicked.connect(self.clear_all_plots)
        controls_layout.addWidget(clear_btn)
        
        # Bouton export
        export_btn = QPushButton("Exporter Données")
        export_btn.clicked.connect(self.export_plot_data)
        controls_layout.addWidget(export_btn)
        
        controls_layout.addStretch()
        
        layout.addWidget(controls_frame)
        
        self.tab_widget.addTab(plots_tab, "Graphiques")
    
    def create_logging_tab(self):
        """Crée l'onglet de journalisation"""
        logging_tab = QWidget()
        layout = QVBoxLayout(logging_tab)
        
        # Configuration logging
        config_group = QGroupBox("Configuration Journalisation")
        config_layout = QGridLayout()
        
        # Répertoire de log
        config_layout.addWidget(QLabel("Répertoire:"), 0, 0)
        self.log_dir_edit = QLineEdit("logs")
        config_layout.addWidget(self.log_dir_edit, 0, 1)
        
        browse_btn = QPushButton("Parcourir")
        browse_btn.clicked.connect(self.browse_log_directory)
        config_layout.addWidget(browse_btn, 0, 2)
        
        # Format de log
        config_layout.addWidget(QLabel("Format:"), 1, 0)
        self.log_format_combo = QComboBox()
        self.log_format_combo.addItems(["CSV", "JSON", "Les deux"])
        config_layout.addWidget(self.log_format_combo, 1, 1)
        
        # Niveau de log
        config_layout.addWidget(QLabel("Niveau:"), 2, 0)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        config_layout.addWidget(self.log_level_combo, 2, 1)
        
        # Bouton appliquer
        apply_btn = QPushButton("Appliquer Configuration")
        apply_btn.clicked.connect(self.apply_log_config)
        config_layout.addWidget(apply_btn, 3, 0, 1, 3)
        
        config_group.setLayout(config_layout)
        
        # Visualisation logs
        view_group = QGroupBox("Visualisation des Logs")
        view_layout = QVBoxLayout()
        
        # Liste des fichiers de log
        self.log_list = QListWidget()
        self.log_list.itemDoubleClicked.connect(self.view_log_file)
        view_layout.addWidget(self.log_list)
        
        # Bouton rafraîchir
        refresh_logs_btn = QPushButton("Rafraîchir la liste")
        refresh_logs_btn.clicked.connect(self.refresh_log_list)
        view_layout.addWidget(refresh_logs_btn)
        
        view_group.setLayout(view_layout)
        
        layout.addWidget(config_group)
        layout.addWidget(view_group)
        
        self.tab_widget.addTab(logging_tab, "Journalisation")
    
    def create_config_tab(self):
        """Crée l'onglet de configuration"""
        config_tab = QWidget()
        layout = QVBoxLayout(config_tab)

        # Configuration des délais
        delays_group = QGroupBox("Délais de communication")
        delays_layout = QGridLayout()
        
        # Délai démarrage périphérique
        delays_layout.addWidget(QLabel("Délai démarrage (s):"), 0, 0)
        self.boot_delay_spin = QSpinBox()
        self.boot_delay_spin.setRange(5, 30)
        self.boot_delay_spin.setValue(10)
        self.boot_delay_spin.setSuffix(" s")
        delays_layout.addWidget(self.boot_delay_spin, 0, 1)
        
        # Délai réponse STATUS
        delays_layout.addWidget(QLabel("Délai STATUS (s):"), 1, 0)
        self.status_delay_spin = QSpinBox()
        self.status_delay_spin.setRange(1, 10)
        self.status_delay_spin.setValue(4)
        self.status_delay_spin.setSuffix(" s")
        delays_layout.addWidget(self.status_delay_spin, 1, 1)
        
        # Délai réponse commandes
        delays_layout.addWidget(QLabel("Délai commandes (s):"), 2, 0)
        self.cmd_delay_spin = QSpinBox()
        self.cmd_delay_spin.setRange(1, 5)
        self.cmd_delay_spin.setValue(2)
        self.cmd_delay_spin.setSuffix(" s")
        delays_layout.addWidget(self.cmd_delay_spin, 2, 1)
        
        # Bouton appliquer
        apply_delays_btn = QPushButton("Appliquer les délais")
        apply_delays_btn.clicked.connect(self.apply_delays)
        delays_layout.addWidget(apply_delays_btn, 3, 0, 1, 2)
        
        delays_group.setLayout(delays_layout)
        
        # Configuration protocole
        proto_group = QGroupBox("Configuration Protocole")
        proto_layout = QFormLayout()
        
        # Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 30)
        self.timeout_spin.setValue(5)
        self.timeout_spin.setSuffix(" s")
        proto_layout.addRow("Timeout commande:", self.timeout_spin)
        
        # Tentatives de reconnexion
        self.reconnect_spin = QSpinBox()
        self.reconnect_spin.setRange(0, 10)
        self.reconnect_spin.setValue(3)
        proto_layout.addRow("Tentatives reconnexion:", self.reconnect_spin)
        
        # Auto-status
        self.auto_status_check = QCheckBox("Requête STATUS automatique")
        self.auto_status_check.setChecked(True)
        proto_layout.addRow(self.auto_status_check)
        
        proto_group.setLayout(proto_layout)
        
        # Sauvegarde/Chargement
        save_group = QGroupBox("Sauvegarde/Chargement")
        save_layout = QHBoxLayout()
        
        save_btn = QPushButton("Sauvegarder Configuration")
        save_btn.clicked.connect(self.save_configuration)
        
        load_btn = QPushButton("Charger Configuration")
        load_btn.clicked.connect(self.load_configuration)
        
        save_layout.addWidget(save_btn)
        save_layout.addWidget(load_btn)
        
        save_group.setLayout(save_layout)
        
        layout.addWidget(proto_group)
        layout.addWidget(save_group)
        layout.addWidget(delays_group)
        layout.addStretch()
        
        self.tab_widget.addTab(config_tab, "Configuration")

    def apply_delays(self):
        """Applique les délais configurés"""
        self.serial_worker.device_boot_delay = self.boot_delay_spin.value()
        self.serial_worker.command_timeout = self.cmd_delay_spin.value() + 1  # +1 pour marge
        self.serial_worker.status_timeout = self.status_delay_spin.value() + 1
        
        QMessageBox.information(self, "Délais mis à jour", 
                              f"Délais appliqués:\n"
                              f"- Démarrage: {self.boot_delay_spin.value()}s\n"
                              f"- STATUS: {self.status_delay_spin.value()}s\n"
                              f"- Commandes: {self.cmd_delay_spin.value()}s")

    def create_diagnostic_tab(self):
        """Crée l'onglet de diagnostic"""
        diag_tab = QWidget()
        layout = QVBoxLayout(diag_tab)
        
        # Section test manuel
        test_group = QGroupBox("Test Manuel")
        test_layout = QGridLayout()
        
        # Champ pour envoyer des données manuelles
        test_layout.addWidget(QLabel("Commande HEX:"), 0, 0)
        self.manual_cmd = QLineEdit()
        self.manual_cmd.setPlaceholderText("Ex: 30 pour HELLO, 38 pour STATUS")
        test_layout.addWidget(self.manual_cmd, 0, 1)
        
        send_manual_btn = QPushButton("Envoyer")
        send_manual_btn.clicked.connect(self.send_manual_command)
        test_layout.addWidget(send_manual_btn, 0, 2)
        
        # Liste des commandes prédéfinies
        test_layout.addWidget(QLabel("Commandes:"), 1, 0)
        self.preset_cmds = QComboBox()
        self.preset_cmds.addItems([
            "HELLO (0x30)",
            "STATUS (0x38)",
            "DELTA=0 (0x31 0x30)",
            "DELTA=5 (0x31 0x35)",
            "OFFSET=0 (0x32 0x30)",
            "MODE MAXI (0x36)",
            "MODE REGUL (0x37)"
        ])
        test_layout.addWidget(self.preset_cmds, 1, 1)
        
        send_preset_btn = QPushButton("Envoyer Prédéfini")
        send_preset_btn.clicked.connect(self.send_preset_command)
        test_layout.addWidget(send_preset_btn, 1, 2)
        
        test_group.setLayout(test_layout)
        
        # Section analyse des réponses
        analyze_group = QGroupBox("Analyse des Réponses")
        analyze_layout = QVBoxLayout()
        
        self.raw_log = QTextEdit()
        self.raw_log.setReadOnly(True)
        self.raw_log.setMaximumHeight(200)
        self.raw_log.setFont(QFont("Courier", 9))
        
        analyze_layout.addWidget(self.raw_log)
        
        # Bouton pour effacer le log
        clear_log_btn = QPushButton("Effacer le Log")
        clear_log_btn.clicked.connect(lambda: self.raw_log.clear())
        analyze_layout.addWidget(clear_log_btn)
        
        analyze_group.setLayout(analyze_layout)
        
        # Section statistiques
        stats_group = QGroupBox("Statistiques")
        stats_layout = QGridLayout()
        
        self.stats_labels = {}
        stats = [
            ("Commandes envoyées", "sent_count"),
            ("Réponses reçues", "received_count"),
            ("Erreurs", "error_count"),
            ("Timeout", "timeout_count"),
            ("Dernière commande", "last_command"),
            ("Dernière réponse", "last_response")
        ]
        
        for i, (label, key) in enumerate(stats):
            stats_layout.addWidget(QLabel(f"{label}:"), i, 0)
            value_label = QLabel("0")
            value_label.setStyleSheet("font: 10pt; background-color: #333; padding: 2px;")
            self.stats_labels[key] = value_label
            stats_layout.addWidget(value_label, i, 1)
        
        stats_group.setLayout(stats_layout)
        
        # Bouton reset statistiques
        reset_stats_btn = QPushButton("Réinitialiser Statistiques")
        reset_stats_btn.clicked.connect(self.reset_diagnostic_stats)
        stats_layout.addWidget(reset_stats_btn, len(stats), 0, 1, 2)
        
        # Assemblage
        layout.addWidget(test_group)
        layout.addWidget(analyze_group)
        layout.addWidget(stats_group)
        
        self.tab_widget.addTab(diag_tab, "Diagnostic")
        
        # Initialiser les statistiques
        self.diagnostic_stats = {
            'sent_count': 0,
            'received_count': 0,
            'error_count': 0,
            'timeout_count': 0,
            'last_command': '',
            'last_response': ''
        }

    def send_manual_command(self):
        """Envoie une commande manuelle"""
        cmd_text = self.manual_cmd.text().strip()
        if not cmd_text:
            return
        
        try:
            # Convertir l'entrée HEX en bytes
            if ' ' in cmd_text:
                # Format: "30 31 32"
                hex_bytes = cmd_text.split()
                cmd_bytes = bytes(int(b, 16) for b in hex_bytes)
            else:
                # Format: "303132" ou "0x303132"
                if cmd_text.startswith('0x'):
                    cmd_text = cmd_text[2:]
                cmd_bytes = bytes.fromhex(cmd_text)
            
            # Envoyer la commande
            #self.serial_worker._send_bytes(cmd_bytes)
            self.serial_worker.serial_port.write(cmd_bytes)
            self.serial_worker.serial_port.flush()

            # Mettre à jour les statistiques
            self.diagnostic_stats['sent_count'] += 1
            self.diagnostic_stats['last_command'] = cmd_bytes.hex()
            self.update_diagnostic_stats()
            
        except Exception as e:
            self.status_bar.showMessage(f"Erreur commande: {str(e)}", 3000)

    def send_preset_command(self):
        """Envoie une commande prédéfinie"""
        cmd_text = self.preset_cmds.currentText()
        
        # Mapper les commandes prédéfinies
        cmd_map = {
            "HELLO (0x30)": b'\x30',
            "STATUS (0x38)": b'\x38',
            "DELTA=0 (0x31 0x30)": b'\x31\x30',
            "DELTA=5 (0x31 0x35)": b'\x31\x35',
            "OFFSET=0 (0x32 0x30)": b'\x32\x30',
            "MODE MAXI (0x36)": b'\x36',
            "MODE REGUL (0x37)": b'\x37'
        }
        
        if cmd_text in cmd_map:
            #self.serial_worker._send_bytes(cmd_map[cmd_text])
            self.serial_worker.serial_port.write(cmd_map[cmd_text])
            self.serial_worker.serial_port.flush()
            
            # Mettre à jour les statistiques
            self.diagnostic_stats['sent_count'] += 1
            self.diagnostic_stats['last_command'] = cmd_map[cmd_text].hex()
            self.update_diagnostic_stats()

    def update_raw_log(self, data):
        """Met à jour le log des données brutes"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        if isinstance(data, bytes):
            hex_str = ' '.join(f'{b:02X}' for b in data)
            ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
            log_entry = f"[{timestamp}] RX: {hex_str:30} | {ascii_str}\n"
        else:
            log_entry = f"[{timestamp}] {data}\n"
        
        self.raw_log.append(log_entry)
        
        # Limiter la taille
        if self.raw_log.document().lineCount() > 1000:
            cursor = self.raw_log.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()

    def update_diagnostic_stats(self):
        """Met à jour les statistiques d'affichage"""
        for key, label in self.stats_labels.items():
            if key in self.diagnostic_stats:
                label.setText(str(self.diagnostic_stats[key]))

    def reset_diagnostic_stats(self):
        """Réinitialise les statistiques"""
        for key in self.diagnostic_stats:
            if key not in ['last_command', 'last_response']:
                self.diagnostic_stats[key] = 0
            else:
                self.diagnostic_stats[key] = ''
        self.update_diagnostic_stats()    

    def refresh_ports(self):
        """Rafraîchit la liste des ports série disponibles"""
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            desc = f"{port.device} - {port.description}"
            self.port_combo.addItem(desc, port.device)
        
        if not ports:
            self.port_combo.addItem("Aucun port détecté", "")
    
    def toggle_connection(self):
        """Connecte/Déconnecte du port série"""
        if self.serial_worker.serial_port and self.serial_worker.serial_port.is_open:
            self.serial_worker.disconnect()
            self.connect_btn.setText("Connecter")
            self.status_timer.stop()
        else:
            port = self.port_combo.currentData()
            baudrate = int(self.baudrate_combo.currentText())
            if port and self.serial_worker.connect(port, baudrate):
                self.connect_btn.setText("Déconnecter")
                self.status_timer.start(self.update_interval.value() * 1000)
    
    def update_display(self, data):
        """Met à jour l'affichage avec les données reçues"""
        timestamp = datetime.now()
        
        # Mettre à jour les labels de statut
        for key, label in self.status_labels.items():
            if key in data:
                value = data[key]
                formatted_value = f"{value:.2f}" if isinstance(value, float) else str(value)
                if label.text() != formatted_value:
                    label.setText(formatted_value)
                
                #label.setText(f"{value:.2f}" if isinstance(value, float) else str(value))
                
                # Ajouter aux données de graphique
                self.plot_data[key].append(value)

        # Mettre à jour les spinbox seulement si les valeurs ont changé
        # et si l'utilisateur n'est pas en train d'éditer
        if 'delta_temp' in data:
            delta_value = int(data['delta_temp'])
            if delta_value != self.delta_spin.value() and not self.delta_spin.hasFocus():
                self.delta_spin.blockSignals(True)
                self.delta_spin.setValue(delta_value)
                self.delta_spin.blockSignals(False)
        
        if 'dew_offset' in data:
            offset_value = int(data['dew_offset'])
            if offset_value != self.offset_spin.value() and not self.offset_spin.hasFocus():
                self.offset_spin.blockSignals(True)
                self.offset_spin.setValue(offset_value)
                self.offset_spin.blockSignals(False)
        
        if 'pwm' in data:
            pwm_value = int(((data['pwm']) * 100) // 255)
            if pwm_value != self.power_spin.value() and not self.power_spin.hasFocus():
                self.power_spin.blockSignals(True)
                self.power_spin.setValue(pwm_value)
                self.power_spin.blockSignals(False)
        
        # Ajouter le timestamp
        self.timestamps.append(timestamp)
        
        # Mettre à jour les graphiques
        if not self.pause_plots_btn.isChecked():
            self.multi_plot.update_data(self.plot_data, list(self.timestamps))
        
        # Mettre à jour la barre de statut
        self.status_label.setText(f"Dernière mise à jour: {timestamp.strftime('%H:%M:%S')}")
    
    def update_status_bar(self, message):
        """Met à jour la barre de statut"""
        self.status_bar.showMessage(message, 3000)
        self.logger.info(message)
    
    def update_raw_console(self, data):
        """Affiche les données brutes en HEX"""
        if data:
            hex_str = ' '.join(f'{b:02X}' for b in data)
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.hex_console.append(f"[{timestamp}] RX: {hex_str}")
            
            # Limiter la taille de la console
            if self.hex_console.document().lineCount() > 100:
                cursor = self.hex_console.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()
    
    def handle_command_ack(self, command, success):
        """Gère les acquittements de commandes"""
        color = "green" if success else "red"
        self.status_bar.showMessage(f"{command}: {'Succès' if success else 'Échec'}", 2000)
        self.logger.info(f"Commande {command}: {'succès' if success else 'échec'}")
    
    def send_mode_command(self):
        """Envoie la commande SET MODE"""
        is_maxi = self.mode_combo.currentText().startswith("Maxi")
        power = self.power_spin.value()
        self.serial_worker.send_mode(is_maxi, power)
    
    def auto_request_status(self):
        """Requête automatique de statut"""
        if (self.serial_worker.serial_port and 
            self.serial_worker.serial_port.is_open and
            self.auto_status_check.isChecked()):
            self.serial_worker.request_status()
    
    def update_status_interval(self):
        """Met à jour l'intervalle de requête STATUS"""
        self.status_timer.setInterval(self.update_interval.value() * 1000)
    
    def toggle_plots_pause(self, paused):
        """Met en pause/reprend les graphiques"""
        self.pause_plots_btn.setText("Reprendre Graphiques" if paused else "Pause Graphiques")
    
    def clear_all_plots(self):
        """Efface tous les graphiques"""
        for data in self.plot_data.values():
            data.clear()
        self.timestamps.clear()
        self.multi_plot.clear_all()
    
    def export_plot_data(self):
        """Exporte les données des graphiques"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exporter les données", "", "CSV Files (*.csv);;All Files (*)"
        )
        if filename:
            try:
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    # En-tête
                    headers = ['Timestamp'] + list(self.plot_data.keys())
                    writer.writerow(headers)
                    
                    # Données
                    for i, ts in enumerate(self.timestamps):
                        row = [ts.strftime("%Y-%m-%d %H:%M:%S.%f")]
                        for key in self.plot_data.keys():
                            if i < len(self.plot_data[key]):
                                row.append(self.plot_data[key][i])
                            else:
                                row.append('')
                        writer.writerow(row)
                
                QMessageBox.information(self, "Export réussi", f"Données exportées vers {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def browse_log_directory(self):
        """Ouvre un dialogue pour choisir le répertoire de log"""
        directory = QFileDialog.getExistingDirectory(self, "Choisir le répertoire de log")
        if directory:
            self.log_dir_edit.setText(directory)
    
    def apply_log_config(self):
        """Applique la configuration de journalisation"""
        # Implémentation simplifiée
        QMessageBox.information(self, "Configuration", "Configuration appliquée")
    
    def refresh_log_list(self):
        """Rafraîchit la liste des fichiers de log"""
        self.log_list.clear()
        try:
            log_dir = self.log_dir_edit.text()
            if os.path.exists(log_dir):
                for file in os.listdir(log_dir):
                    if file.endswith(('.csv', '.json', '.log')):
                        self.log_list.addItem(file)
        except Exception as e:
            self.logger.error(f"Erreur rafraîchissement logs: {e}")
    
    def view_log_file(self, item):
        """Ouvre un fichier de log pour visualisation"""
        filename = item.text()
        log_path = os.path.join(self.log_dir_edit.text(), filename)
        
        if os.path.exists(log_path):
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Log: {filename}")
            dialog.resize(800, 600)
            
            layout = QVBoxLayout(dialog)
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setFont(QFont("Courier", 9))
            
            try:
                with open(log_path, 'r') as f:
                    text_edit.setText(f.read())
            except Exception as e:
                text_edit.setText(f"Erreur lecture: {str(e)}")
            
            layout.addWidget(text_edit)
            dialog.exec()
    
    def save_configuration(self):
        """Sauvegarde la configuration"""
        config = {
            'port': self.port_combo.currentData(),
            'baudrate': self.baudrate_combo.currentText(),
            'delta_temp': self.delta_spin.value(),
            'dew_offset': self.offset_spin.value(),
            'mode': self.mode_combo.currentIndex(),
            'power': self.power_spin.value(),
            'update_interval': self.update_interval.value(),
            'log_directory': self.log_dir_edit.text(),
            'log_format': self.log_format_combo.currentIndex(),
            'log_level': self.log_level_combo.currentIndex(),
            'timeout': self.timeout_spin.value(),
            'reconnect_attempts': self.reconnect_spin.value(),
            'auto_status': self.auto_status_check.isChecked()
        }
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder configuration", "", "JSON Files (*.json)"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)
                QMessageBox.information(self, "Sauvegarde", "Configuration sauvegardée")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur sauvegarde: {str(e)}")
    
    def load_configuration(self):
        """Charge la configuration"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Charger configuration", "", "JSON Files (*.json)"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                # Appliquer la configuration
                self.baudrate_combo.setCurrentText(str(config.get('baudrate', '19200')))
                self.delta_spin.setValue(config.get('delta_temp', 0))
                self.offset_spin.setValue(config.get('dew_offset', 0))
                self.mode_combo.setCurrentIndex(config.get('mode', 0))
                self.power_spin.setValue(config.get('power', 100))
                self.update_interval.setValue(config.get('update_interval', 5))
                self.log_dir_edit.setText(config.get('log_directory', 'logs'))
                self.log_format_combo.setCurrentIndex(config.get('log_format', 0))
                self.log_level_combo.setCurrentIndex(config.get('log_level', 1))
                self.timeout_spin.setValue(config.get('timeout', 5))
                self.reconnect_spin.setValue(config.get('reconnect_attempts', 3))
                self.auto_status_check.setChecked(config.get('auto_status', True))
                
                QMessageBox.information(self, "Chargement", "Configuration chargée")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur chargement: {str(e)}")
    
    def closeEvent(self, event):
        """Gère la fermeture de l'application"""
        self.serial_worker.disconnect()
        self.worker_thread.quit()
        self.worker_thread.wait()
        
        # Sauvegarder l'état
        try:
            with open('app_state.json', 'w') as f:
                json.dump({
                    'window_geometry': {
                        'x': self.x(),
                        'y': self.y(),
                        'width': self.width(),
                        'height': self.height()
                    },
                    'current_tab': self.tab_widget.currentIndex()
                }, f)
        except:
            pass
        
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Style moderne
    app.setStyle('Fusion')
    
    # Palette de couleurs
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)
    
    window = MainWindow()
    
    # Restaurer la géométrie de la fenêtre
    try:
        with open('app_state.json', 'r') as f:
            state = json.load(f)
            geo = state.get('window_geometry', {})
            window.setGeometry(geo.get('x', 100), geo.get('y', 100),
                              geo.get('width', 1400), geo.get('height', 900))
            window.tab_widget.setCurrentIndex(state.get('current_tab', 0))
    except:
        pass
    
    window.show()
    sys.exit(app.exec())