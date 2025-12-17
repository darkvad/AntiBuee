import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from collections import deque
from datetime import datetime

class RealTimePlot(pg.PlotWidget):
    """Widget de graphique temps réel amélioré"""
    
    def __init__(self, title="Graphique", y_label="Valeur", color='blue', max_points=1000):
        super().__init__()
        
        self.title = title
        self.color = color
        self.max_points = max_points
        self.data = deque(maxlen=max_points)
        self.timestamps = deque(maxlen=max_points)
        self.paused = False
        
        self.setup_plot()
        self.setup_controls()
    
    def setup_plot(self):
        """Configure l'apparence du graphique"""
        self.setBackground('w')
        self.setLabel('left', self.title)
        self.setLabel('bottom', 'Temps')
        self.showGrid(x=True, y=True, alpha=0.3)
        self.setTitle(self.title, color='k', size='12pt')
        
        # Courbe principale
        self.curve = self.plot(pen=pg.mkPen(color=self.color, width=2))
        
        # Courbe de moyenne mobile
        self.avg_curve = self.plot(
            pen=pg.mkPen(color='red', width=1, style=Qt.PenStyle.DashLine)
        )
        
        # Dernière valeur
        self.last_value_text = pg.TextItem("", anchor=(1, 0))
        self.last_value_text.setColor(self.color)
        self.addItem(self.last_value_text)
        
        # Ligne horizontale pour la dernière valeur
        self.hline = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(color=self.color, width=1, style=Qt.PenStyle.DashLine))
        self.addItem(self.hline)
    
    def setup_controls(self):
        """Configure les contrôles du graphique"""
        # Menu contextuel
        self.setMenuEnabled(True)
        
        # Axe X avec temps
        self.getAxis('bottom').enableAutoSIPrefix(False)
    
    def add_data_point(self, value, timestamp=None):
        """Ajoute un point de données"""
        if self.paused:
            return
        
        if timestamp is None:
            timestamp = datetime.now()
        
        self.data.append(value)
        self.timestamps.append(timestamp)
        
        if len(self.data) > 1:
            self.update_plot()
            self.update_stats()
    
    def update_plot(self):
        """Met à jour le graphique"""
        if len(self.data) == 0:
            return
        
        # Convertir les timestamps en secondes relatives
        if isinstance(self.timestamps[0], datetime):
            base_time = self.timestamps[0]
            x = [(t - base_time).total_seconds() for t in self.timestamps]
        else:
            x = list(range(len(self.data)))
        
        y = list(self.data)
        
        # Mettre à jour la courbe principale
        self.curve.setData(x, y)
        
        # Calculer et afficher la moyenne mobile
        if len(y) >= 10:
            window = min(20, len(y))
            weights = np.ones(window) / window
            avg_y = np.convolve(y, weights, mode='valid')
            avg_x = x[window-1:]
            self.avg_curve.setData(avg_x, avg_y)
        
        # Mettre à jour la dernière valeur
        if len(y) > 0:
            last_val = y[-1]
            self.last_value_text.setText(f"{last_val:.2f}")
            self.last_value_text.setPos(x[-1], last_val)
            
            # Mettre à jour la ligne horizontale
            self.hline.setValue(last_val)
        
        # Ajuster la vue
        if len(x) > 0:
            self.setXRange(max(0, x[-1] - 60), x[-1] + 5)
            
            # Ajuster l'échelle Y avec une marge
            if len(y) > 0:
                y_min, y_max = min(y), max(y)
                margin = (y_max - y_min) * 0.1
                self.setYRange(y_min - margin, y_max + margin)
    
    def update_stats(self):
        """Met à jour les statistiques affichées"""
        if len(self.data) == 0:
            return
        
        data_array = np.array(self.data)
        stats = {
            'min': np.min(data_array),
            'max': np.max(data_array),
            'mean': np.mean(data_array),
            'std': np.std(data_array),
            'last': data_array[-1]
        }
        
        # Mettre à jour le titre avec les stats
        stats_text = f"{self.title} | Dernier: {stats['last']:.2f} | Min: {stats['min']:.2f} | Max: {stats['max']:.2f}"
        self.setTitle(stats_text)
    
    def clear(self):
        """Efface les données du graphique"""
        self.data.clear()
        self.timestamps.clear()
        self.curve.clear()
        self.avg_curve.clear()
        self.last_value_text.setText("")
    
    def toggle_pause(self):
        """Met en pause/reprend le graphique"""
        self.paused = not self.paused
    
    def set_paused(self, paused):
        """Définit l'état de pause"""
        self.paused = paused

class MultiPlotWidget(QWidget):
    """Widget contenant plusieurs graphiques"""
    
    def __init__(self):
        super().__init__()
        
        self.plots = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        
        # Onglets pour différents groupes de graphiques
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Onglet Températures
        temp_tab = QWidget()
        temp_layout = QGridLayout(temp_tab)
        
        self.plots['temperature'] = RealTimePlot("Température Extérieure", "°C", 'red')
        self.plots['tube_temperature'] = RealTimePlot("Température Tube", "°C", 'orange')
        self.plots['dew_point'] = RealTimePlot("Point de Rosée", "°C", 'blue')
        self.plots['humidity'] = RealTimePlot("Humidité", "%", 'green')
        
        temp_layout.addWidget(self.plots['temperature'], 0, 0)
        temp_layout.addWidget(self.plots['tube_temperature'], 0, 1)
        temp_layout.addWidget(self.plots['dew_point'], 1, 0)
        temp_layout.addWidget(self.plots['humidity'], 1, 1)
        
        self.tab_widget.addTab(temp_tab, "Températures")
        
        # Onglet Autres mesures
        other_tab = QWidget()
        other_layout = QGridLayout(other_tab)
        
        self.plots['humidity'] = RealTimePlot("Humidité", "%", 'green')
        self.plots['pwm'] = RealTimePlot("Puissance PWM", "", 'purple')
        self.plots['delta_temp'] = RealTimePlot("Delta Temp", "", 'cyan')
        self.plots['dew_offset'] = RealTimePlot("Offset Rosée", "", 'magenta')
        
        other_layout.addWidget(self.plots['humidity'], 0, 0)
        other_layout.addWidget(self.plots['pwm'], 0, 1)
        other_layout.addWidget(self.plots['delta_temp'], 1, 0)
        other_layout.addWidget(self.plots['dew_offset'], 1, 1)
        
        self.tab_widget.addTab(other_tab, "Autres Mesures")
        
        # Contrôles
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        
        # Bouton pause tous
        self.pause_all_btn = QPushButton("Pause Tous")
        self.pause_all_btn.setCheckable(True)
        self.pause_all_btn.toggled.connect(self.toggle_all_plots)
        controls_layout.addWidget(self.pause_all_btn)
        
        # Bouton effacer tous
        clear_all_btn = QPushButton("Effacer Tous")
        clear_all_btn.clicked.connect(self.clear_all)
        controls_layout.addWidget(clear_all_btn)
        
        # Sélecteur d'échelle de temps
        controls_layout.addWidget(QLabel("Échelle temps:"))
        self.time_scale = QComboBox()
        self.time_scale.addItems(["30s", "1min", "5min", "15min", "1h"])
        self.time_scale.currentTextChanged.connect(self.change_time_scale)
        controls_layout.addWidget(self.time_scale)
        
        controls_layout.addStretch()
        layout.addWidget(controls_frame)
    
    def update_data(self, data_dict, timestamps):
        """Met à jour tous les graphiques avec de nouvelles données"""
        for key, plot in self.plots.items():
            if key in data_dict and len(data_dict[key]) > 0:
                # Utiliser les dernières valeurs
                values = list(data_dict[key])
                times = timestamps[-len(values):] if len(timestamps) >= len(values) else timestamps
                
                # Mettre à jour le graphique
                if len(values) == len(times):
                    plot.data.clear()
                    plot.timestamps.clear()
                    for val, ts in zip(values, times):
                        plot.add_data_point(val, ts)
    
    def clear_all(self):
        """Efface tous les graphiques"""
        for plot in self.plots.values():
            plot.clear()
    
    def toggle_all_plots(self, paused):
        """Met en pause/reprend tous les graphiques"""
        for plot in self.plots.values():
            plot.set_paused(paused)
        self.pause_all_btn.setText("Reprendre Tous" if paused else "Pause Tous")
    
    def change_time_scale(self, scale):
        """Change l'échelle de temps des graphiques"""
        scale_seconds = {
            "30s": 30,
            "1min": 60,
            "5min": 300,
            "15min": 900,
            "1h": 3600
        }
        
        seconds = scale_seconds.get(scale, 60)
        for plot in self.plots.values():
            plot.setXRange(0, seconds)