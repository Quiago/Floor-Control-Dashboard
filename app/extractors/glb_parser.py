# app/extractors/glb_parser.py
import struct
import json
from typing import List, Dict, Tuple
from pathlib import Path


def parse_glb(filepath: str) -> Dict:
    """Extract equipment nodes from GLB file"""
    with open(filepath, 'rb') as f:
        # GLB header
        magic = f.read(4)
        if magic != b'glTF':
            raise ValueError("Invalid GLB file")
        
        version = struct.unpack('<I', f.read(4))[0]
        length = struct.unpack('<I', f.read(4))[0]
        
        # JSON chunk
        json_length = struct.unpack('<I', f.read(4))[0]
        json_type = f.read(4)
        json_data = f.read(json_length)
        gltf = json.loads(json_data)
    
    equipment = []
    for idx, node in enumerate(gltf['nodes']):
        name = node.get('name', '')
        
        # Skip visual helpers
        if not name or any(x in name for x in ['geo_', 'Object_', 'root', 'Scene']):
            continue
            
        # Extract equipment type from name
        eq_type = _classify_equipment(name)
        if eq_type == 'unknown' and '_Link' in name:
            continue
            
        equipment.append({
            'id': str(idx),
            'name': name,
            'type': eq_type,
            'position': node.get('translation', [0, 0, 0])
        })
    
    return {'equipment': equipment, 'total': len(equipment)}


def _classify_equipment(name: str) -> str:
    """Classify equipment by name pattern"""
    name_lower = name.lower()
    
    patterns = {
        'analyzer': 'analyzer',
        'cartesian': 'robot',
        'centrifuge': 'centrifuge',
        'storage': 'storage',
        'conveyor': 'conveyor',
        'mixer': 'mixer',
        'pump': 'pump'
    }
    
    for pattern, eq_type in patterns.items():
        if pattern in name_lower:
            return eq_type
    
    return 'unknown'


def load_equipment_from_glb(glb_path: str = "assets/pharmaceutical_manufacturing_machinery.glb") -> List[Dict]:
    """Load and enrich equipment from GLB file"""
    if not Path(glb_path).exists():
        return []
    
    data = parse_glb(glb_path)
    equipment_list = []
    
    for eq in data['equipment']:
        enriched = {
            **eq,
            'sensors': get_sensors_for_type(eq['type']),
            'label': eq['name'].replace('_', ' ').title()
        }
        equipment_list.append(enriched)
    
    return equipment_list


def get_sensors_for_type(eq_type: str) -> List[Dict]:
    """Get sensor definitions for equipment type"""
    sensor_db = {
        'analyzer': [
            {'id': 'temp', 'name': 'Temperature', 'unit': '°C', 'range': [15, 30]},
            {'id': 'ph', 'name': 'pH Level', 'unit': 'pH', 'range': [6.5, 7.5]},
            {'id': 'turbidity', 'name': 'Turbidity', 'unit': 'NTU', 'range': [0, 5]}
        ],
        'robot': [
            {'id': 'x_pos', 'name': 'X Position', 'unit': 'mm', 'range': [0, 2000]},
            {'id': 'y_pos', 'name': 'Y Position', 'unit': 'mm', 'range': [0, 1500]},
            {'id': 'vibration', 'name': 'Vibration', 'unit': 'mm/s', 'range': [0, 5]},
            {'id': 'current', 'name': 'Motor Current', 'unit': 'A', 'range': [0.5, 2.0]}
        ],
        'centrifuge': [
            {'id': 'rpm', 'name': 'RPM', 'unit': 'RPM', 'range': [3000, 5000]},
            {'id': 'vibration', 'name': 'Vibration', 'unit': 'mm/s', 'range': [0, 3]},
            {'id': 'temp', 'name': 'Temperature', 'unit': '°C', 'range': [20, 35]}
        ],
        'storage': [
            {'id': 'level', 'name': 'Fill Level', 'unit': '%', 'range': [20, 90]},
            {'id': 'temp', 'name': 'Temperature', 'unit': '°C', 'range': [15, 25]},
            {'id': 'humidity', 'name': 'Humidity', 'unit': '%RH', 'range': [30, 60]}
        ],
        'conveyor': [
            {'id': 'speed', 'name': 'Belt Speed', 'unit': 'm/min', 'range': [5, 30]},
            {'id': 'current', 'name': 'Motor Current', 'unit': 'A', 'range': [1, 3]},
            {'id': 'vibration', 'name': 'Vibration', 'unit': 'mm/s', 'range': [0, 2]}
        ]
    }
    
    return sensor_db.get(eq_type, [
        {'id': 'temp', 'name': 'Temperature', 'unit': '°C', 'range': [0, 100]}
    ])