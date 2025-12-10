// src/utils/glbParser.js
// Equipment extraction from GLB model (simplified for frontend)

// Equipment data extracted from the GLB model
// In production, this would be parsed from the actual GLB file
// For now, we provide static data based on the model analysis
export const EQUIPMENT_DATA = [
    { id: '1', name: 'Centrifuge_01', type: 'centrifuge', label: 'Centrifuge 01' },
    { id: '2', name: 'Centrifuge_02', type: 'centrifuge', label: 'Centrifuge 02' },
    { id: '3', name: 'Analyzer_Chemical_01', type: 'analyzer', label: 'Chemical Analyzer 01' },
    { id: '4', name: 'Analyzer_Spectral_01', type: 'analyzer', label: 'Spectral Analyzer 01' },
    { id: '5', name: 'Cartesian_Robot_01', type: 'robot', label: 'Cartesian Robot 01' },
    { id: '6', name: 'Cartesian_Robot_02', type: 'robot', label: 'Cartesian Robot 02' },
    { id: '7', name: 'Storage_Tank_01', type: 'storage', label: 'Storage Tank 01' },
    { id: '8', name: 'Storage_Tank_02', type: 'storage', label: 'Storage Tank 02' },
    { id: '9', name: 'Conveyor_Main', type: 'conveyor', label: 'Main Conveyor' },
    { id: '10', name: 'Conveyor_Secondary', type: 'conveyor', label: 'Secondary Conveyor' },
    { id: '11', name: 'Mixer_01', type: 'mixer', label: 'Mixer 01' },
    { id: '12', name: 'Pump_01', type: 'pump', label: 'Pump 01' },
];

// Sensor definitions by equipment type
const SENSOR_DB = {
    analyzer: [
        { id: 'temp', name: 'Temperature', unit: '°C', range: [15, 30] },
        { id: 'ph', name: 'pH Level', unit: 'pH', range: [6.5, 7.5] },
        { id: 'turbidity', name: 'Turbidity', unit: 'NTU', range: [0, 5] },
    ],
    robot: [
        { id: 'x_pos', name: 'X Position', unit: 'mm', range: [0, 2000] },
        { id: 'y_pos', name: 'Y Position', unit: 'mm', range: [0, 1500] },
        { id: 'vibration', name: 'Vibration', unit: 'mm/s', range: [0, 5] },
        { id: 'current', name: 'Motor Current', unit: 'A', range: [0.5, 2.0] },
    ],
    centrifuge: [
        { id: 'rpm', name: 'RPM', unit: 'RPM', range: [3000, 5000] },
        { id: 'vibration', name: 'Vibration', unit: 'mm/s', range: [0, 3] },
        { id: 'temp', name: 'Temperature', unit: '°C', range: [20, 35] },
    ],
    storage: [
        { id: 'level', name: 'Fill Level', unit: '%', range: [20, 90] },
        { id: 'temp', name: 'Temperature', unit: '°C', range: [15, 25] },
        { id: 'humidity', name: 'Humidity', unit: '%RH', range: [30, 60] },
    ],
    conveyor: [
        { id: 'speed', name: 'Belt Speed', unit: 'm/min', range: [5, 30] },
        { id: 'current', name: 'Motor Current', unit: 'A', range: [1, 3] },
        { id: 'vibration', name: 'Vibration', unit: 'mm/s', range: [0, 2] },
    ],
    mixer: [
        { id: 'rpm', name: 'RPM', unit: 'RPM', range: [50, 500] },
        { id: 'temp', name: 'Temperature', unit: '°C', range: [20, 80] },
        { id: 'torque', name: 'Torque', unit: 'Nm', range: [0, 100] },
    ],
    pump: [
        { id: 'flow', name: 'Flow Rate', unit: 'L/min', range: [0, 100] },
        { id: 'pressure', name: 'Pressure', unit: 'bar', range: [0, 10] },
        { id: 'current', name: 'Motor Current', unit: 'A', range: [0.5, 5] },
    ],
};

export function getSensorsForType(equipmentType) {
    return SENSOR_DB[equipmentType] || [
        { id: 'temp', name: 'Temperature', unit: '°C', range: [0, 100] },
    ];
}

export function loadEquipmentFromGLB() {
    // Return enriched equipment data
    return EQUIPMENT_DATA.map(eq => ({
        ...eq,
        sensors: getSensorsForType(eq.type),
    }));
}

export function classifyEquipment(name) {
    const nameLower = name.toLowerCase();
    const patterns = {
        analyzer: 'analyzer',
        cartesian: 'robot',
        centrifuge: 'centrifuge',
        storage: 'storage',
        conveyor: 'conveyor',
        mixer: 'mixer',
        pump: 'pump',
    };

    for (const [pattern, type] of Object.entries(patterns)) {
        if (nameLower.includes(pattern)) {
            return type;
        }
    }
    return 'unknown';
}
