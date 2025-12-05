# app/services/sensor_simulator.py
"""
Sensor Data Simulator for Demo and Testing.

Generates realistic sensor data with configurable anomalies
for testing workflow triggers without real equipment.
"""
import random
import math
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from .database import db


class AnomalyType(Enum):
    """Types of anomalies that can be injected."""
    SPIKE = "spike"           # Sudden spike above threshold
    DRIFT = "drift"           # Gradual increase over time
    OSCILLATION = "oscillation"  # Fluctuating values
    FLATLINE = "flatline"     # Stuck at a single value
    RANDOM = "random"         # Random anomaly selection


@dataclass
class SensorConfig:
    """Configuration for a simulated sensor."""
    equipment_id: str
    sensor_type: str
    unit: str
    min_normal: float
    max_normal: float
    current_value: float = 0.0
    noise_level: float = 0.05  # 5% noise by default
    
    def __post_init__(self):
        self.current_value = random.uniform(self.min_normal, self.max_normal)


@dataclass
class SimulationState:
    """State of a running simulation."""
    sensors: Dict[str, SensorConfig] = field(default_factory=dict)
    anomaly_active: bool = False
    anomaly_type: Optional[AnomalyType] = None
    anomaly_sensor: Optional[str] = None
    anomaly_start_time: Optional[datetime] = None
    tick_count: int = 0


class SensorSimulator:
    """
    Simulates sensor data for equipment.
    
    Features:
    - Generates realistic base values with noise
    - Supports anomaly injection for testing alerts
    - Logs readings to database for historical analysis
    """
    
    # Default sensor configurations by equipment type
    SENSOR_DEFAULTS = {
        'analyzer': [
            ('temp', '°C', 18, 28),
            ('ph', 'pH', 6.8, 7.2),
            ('turbidity', 'NTU', 0.5, 3.0),
            ('conductivity', 'µS/cm', 200, 400)
        ],
        'robot': [
            ('x_pos', 'mm', 0, 2000),
            ('y_pos', 'mm', 0, 1500),
            ('z_pos', 'mm', 0, 1000),
            ('vibration', 'mm/s', 0.5, 2.5),
            ('current', 'A', 0.8, 1.5),
            ('cycle_time', 's', 2, 8)
        ],
        'centrifuge': [
            ('rpm', 'RPM', 3500, 4500),
            ('vibration', 'mm/s', 0.3, 1.5),
            ('temp', '°C', 22, 32),
            ('imbalance', 'g', 0, 5)
        ],
        'storage': [
            ('level', '%', 30, 80),
            ('temp', '°C', 18, 23),
            ('humidity', '%RH', 35, 55),
            ('pressure', 'bar', 0.95, 1.05)
        ],
        'conveyor': [
            ('speed', 'm/min', 10, 25),
            ('current', 'A', 1.2, 2.5),
            ('vibration', 'mm/s', 0.2, 1.0),
            ('tension', 'N', 200, 400)
        ]
    }
    
    def __init__(self):
        self.state = SimulationState()
        self._anomaly_callbacks: List[Callable] = []
    
    def register_equipment(self, equipment_id: str, equipment_type: str) -> List[str]:
        """
        Register equipment with default sensors based on type.
        
        Returns list of sensor keys (equipment_id.sensor_type).
        """
        sensor_keys = []
        
        sensor_configs = self.SENSOR_DEFAULTS.get(equipment_type, [])
        
        for sensor_type, unit, min_val, max_val in sensor_configs:
            key = f"{equipment_id}.{sensor_type}"
            self.state.sensors[key] = SensorConfig(
                equipment_id=equipment_id,
                sensor_type=sensor_type,
                unit=unit,
                min_normal=min_val,
                max_normal=max_val
            )
            sensor_keys.append(key)
        
        return sensor_keys
    
    def tick(self) -> Dict[str, float]:
        """
        Advance simulation by one tick.
        
        Returns current sensor values.
        """
        self.state.tick_count += 1
        values = {}
        
        for key, sensor in self.state.sensors.items():
            # Check if this sensor has an active anomaly
            if self.state.anomaly_active and self.state.anomaly_sensor == key:
                new_value = self._generate_anomaly_value(sensor)
            else:
                new_value = self._generate_normal_value(sensor)
            
            sensor.current_value = new_value
            values[key] = new_value
            
            # Log to database
            db.log_sensor_reading(
                equipment_id=sensor.equipment_id,
                sensor_type=sensor.sensor_type,
                value=new_value,
                unit=sensor.unit
            )
        
        return values
    
    def _generate_normal_value(self, sensor: SensorConfig) -> float:
        """Generate a normal value with small random noise."""
        center = (sensor.min_normal + sensor.max_normal) / 2
        range_size = sensor.max_normal - sensor.min_normal
        
        # Add sinusoidal drift for more realistic behavior
        drift = math.sin(self.state.tick_count * 0.1) * range_size * 0.1
        
        # Add random noise
        noise = random.gauss(0, range_size * sensor.noise_level)
        
        value = center + drift + noise
        
        # Clamp to normal range with small margin
        margin = range_size * 0.1
        return max(sensor.min_normal - margin, min(sensor.max_normal + margin, value))
    
    def _generate_anomaly_value(self, sensor: SensorConfig) -> float:
        """Generate an anomalous value based on current anomaly type."""
        range_size = sensor.max_normal - sensor.min_normal
        
        if self.state.anomaly_type == AnomalyType.SPIKE:
            # Spike: 150-200% of max value
            return sensor.max_normal * random.uniform(1.5, 2.0)
        
        elif self.state.anomaly_type == AnomalyType.DRIFT:
            # Drift: gradually increase based on tick count since anomaly start
            if self.state.anomaly_start_time:
                elapsed = (datetime.now() - self.state.anomaly_start_time).total_seconds()
                drift_factor = min(elapsed / 30.0, 1.0)  # Full drift in 30 seconds
                return sensor.max_normal + (range_size * drift_factor)
            return sensor.max_normal * 1.2
        
        elif self.state.anomaly_type == AnomalyType.OSCILLATION:
            # Oscillation: rapidly fluctuating values
            osc = math.sin(self.state.tick_count * 2.0) * range_size
            return sensor.max_normal + osc
        
        elif self.state.anomaly_type == AnomalyType.FLATLINE:
            # Flatline: stuck at a specific value (possibly indicates sensor failure)
            return sensor.max_normal * 1.1
        
        # Default: spike
        return sensor.max_normal * 1.5
    
    def inject_anomaly(self, sensor_key: str, anomaly_type: AnomalyType = AnomalyType.SPIKE):
        """
        Inject an anomaly for a specific sensor.
        
        Args:
            sensor_key: Key in format "equipment_id.sensor_type"
            anomaly_type: Type of anomaly to inject
        """
        if sensor_key not in self.state.sensors:
            raise ValueError(f"Unknown sensor: {sensor_key}")
        
        self.state.anomaly_active = True
        self.state.anomaly_type = anomaly_type
        self.state.anomaly_sensor = sensor_key
        self.state.anomaly_start_time = datetime.now()
        
        print(f"[SIMULATOR] Injected {anomaly_type.value} anomaly on {sensor_key}")
    
    def clear_anomaly(self):
        """Clear any active anomaly."""
        self.state.anomaly_active = False
        self.state.anomaly_type = None
        self.state.anomaly_sensor = None
        self.state.anomaly_start_time = None
        print("[SIMULATOR] Anomaly cleared")
    
    def get_current_values(self) -> Dict[str, float]:
        """Get current values without advancing simulation."""
        return {key: sensor.current_value for key, sensor in self.state.sensors.items()}
    
    def get_sensor_info(self, sensor_key: str) -> Optional[Dict]:
        """Get information about a sensor."""
        sensor = self.state.sensors.get(sensor_key)
        if not sensor:
            return None
        
        return {
            'equipment_id': sensor.equipment_id,
            'sensor_type': sensor.sensor_type,
            'unit': sensor.unit,
            'current_value': sensor.current_value,
            'min_normal': sensor.min_normal,
            'max_normal': sensor.max_normal,
            'is_anomaly': (
                self.state.anomaly_active and 
                self.state.anomaly_sensor == sensor_key
            )
        }
    
    def generate_demo_data(self, equipment_configs: List[Dict]) -> Dict[str, float]:
        """
        Generate demo data for a list of equipment.
        
        Args:
            equipment_configs: List of {'id': str, 'type': str}
        
        Returns:
            Dict of sensor_key -> value
        """
        # Register all equipment
        for eq in equipment_configs:
            self.register_equipment(eq['id'], eq['type'])
        
        # Generate one tick of data
        return self.tick()
    
    def generate_triggering_data(self, workflow_nodes: List[Dict]) -> Dict[str, float]:
        """
        Generate data that will trigger conditions in workflow nodes.
        
        Analyzes node configurations and generates values that exceed thresholds.
        
        Args:
            workflow_nodes: List of workflow nodes with config
        
        Returns:
            Dict of sensor_key -> value (some will be triggering values)
        """
        data = {}
        
        for node in workflow_nodes:
            config = node.get('data', {}).get('config', {})
            if not config:
                continue
            
            equipment_id = config.get('equipment_id', node.get('id', ''))
            sensor_type = config.get('sensor_type', '')
            operator = config.get('operator', '>')
            threshold = config.get('threshold', 0)
            
            if not sensor_type:
                continue
            
            sensor_key = f"{equipment_id}.{sensor_type}"
            
            # Generate a value that triggers the condition
            if operator in ('>', '>='):
                # Value above threshold
                data[sensor_key] = threshold + random.uniform(5, 20)
            elif operator in ('<', '<='):
                # Value below threshold
                data[sensor_key] = threshold - random.uniform(5, 20)
            elif operator == '==':
                # Exact value (with tiny variation)
                data[sensor_key] = threshold + random.uniform(-0.01, 0.01)
            elif operator == 'between':
                threshold_max = config.get('threshold_max', threshold + 10)
                # Value outside the range
                data[sensor_key] = threshold_max + random.uniform(5, 10)
            else:
                # Default: exceed threshold
                data[sensor_key] = threshold * 1.5
        
        return data


# Global instance
sensor_simulator = SensorSimulator()

