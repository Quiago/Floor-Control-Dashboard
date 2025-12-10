// src/services/sensorSimulator.js
// Sensor data simulation service

/**
 * Generate simulated sensor data based on configured nodes.
 * 
 * @param {Array} nodes - Workflow nodes with configuration
 * @param {number} tick - Current simulation tick number
 * @returns {Object} { dataDict: {sensorKey: value}, dataList: [{key, value, threshold, equipment, ...}] }
 */
export function generateSensorData(nodes, tick) {
    const dataDict = {};
    const dataList = [];

    for (const node of nodes) {
        if (node.data?.is_action) continue;

        const config = node.data?.config || {};
        if (!config.sensor_type) continue;

        const equipmentId = config.equipment_id || node.id;
        const sensorType = config.sensor_type;
        const threshold = parseFloat(config.threshold) || 50;

        const sensorKey = `${equipmentId}.${sensorType}`;

        // Generate value that oscillates around 80% of threshold
        const baseValue = threshold * 0.8;
        const noise = (Math.random() - 0.5) * threshold * 0.2;
        const oscillation = Math.sin(tick * 0.3) * threshold * 0.15;

        let value = baseValue + noise + oscillation;

        // Every 8 ticks, create a spike that exceeds threshold
        if (tick % 8 === 0) {
            value = threshold * (1.1 + Math.random() * 0.2);
        }

        value = Math.round(value * 100) / 100;
        dataDict[sensorKey] = value;

        // Pre-compute display values
        const isAlert = value > threshold;
        const progressPct = threshold > 0
            ? Math.min(100, Math.round((value / threshold) * 100))
            : 0;
        const status = isAlert ? 'alert' : (progressPct > 80 ? 'warning' : 'normal');

        dataList.push({
            key: sensorType,
            value,
            threshold,
            equipment: node.data?.label || equipmentId,
            is_alert: isAlert,
            progress_pct: progressPct,
            status,
        });
    }

    return { dataDict, dataList };
}

/**
 * Generate a single reading with anomaly injection.
 * 
 * @param {string} sensorType - Type of sensor
 * @param {Object} range - {min, max} normal range
 * @param {string|null} anomalyType - 'spike', 'drift', 'oscillation', 'flatline', or null
 * @param {number} tick - Current tick for time-based anomalies
 * @returns {number} Sensor value
 */
export function generateReading(sensorType, range, anomalyType = null, tick = 0) {
    const { min, max } = range;
    const mid = (min + max) / 2;
    const span = max - min;

    let value;

    switch (anomalyType) {
        case 'spike':
            // Random spikes above max
            value = max + Math.random() * span * 0.5;
            break;
        case 'drift':
            // Gradual drift upward
            value = mid + (tick * 0.1) % span;
            break;
        case 'oscillation':
            // Rapid oscillation
            value = mid + Math.sin(tick) * span * 0.8;
            break;
        case 'flatline':
            // Stuck at a constant value
            value = mid;
            break;
        default:
            // Normal value with small noise
            value = mid + (Math.random() - 0.5) * span * 0.6;
    }

    return Math.round(value * 100) / 100;
}

/**
 * Get value color based on thresholds.
 * 
 * @param {number} value - Current value
 * @param {number} threshold - Alert threshold
 * @param {number} warningRatio - Ratio for warning (default 0.8)
 * @returns {string} 'normal' | 'warning' | 'alert'
 */
export function getValueStatus(value, threshold, warningRatio = 0.8) {
    if (value >= threshold) return 'alert';
    if (value >= threshold * warningRatio) return 'warning';
    return 'normal';
}

const sensorSimulator = {
    generateSensorData,
    generateReading,
    getValueStatus,
};

export default sensorSimulator;
