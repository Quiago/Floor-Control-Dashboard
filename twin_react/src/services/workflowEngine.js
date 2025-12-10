// src/services/workflowEngine.js
// Workflow condition evaluation engine

export const ConditionOperator = {
    GREATER_THAN: '>',
    LESS_THAN: '<',
    EQUALS: '==',
    NOT_EQUALS: '!=',
    GREATER_OR_EQUAL: '>=',
    LESS_OR_EQUAL: '<=',
    BETWEEN: 'between',
    NOT_BETWEEN: 'not_between',
};

/**
 * Evaluate a threshold condition.
 * 
 * @param {number} value - Current sensor value
 * @param {string} operator - Comparison operator
 * @param {number} threshold - Threshold value (or min for between)
 * @param {number|null} thresholdMax - Max value for between operators
 * @returns {boolean} True if condition is met (alert should trigger)
 */
export function evaluateCondition(value, operator, threshold, thresholdMax = null) {
    try {
        switch (operator) {
            case '>':
                return value > threshold;
            case '<':
                return value < threshold;
            case '==':
                return Math.abs(value - threshold) < 0.0001;
            case '!=':
                return Math.abs(value - threshold) >= 0.0001;
            case '>=':
                return value >= threshold;
            case '<=':
                return value <= threshold;
            case 'between':
                return threshold <= value && value <= (thresholdMax || threshold);
            case 'not_between':
                return !(threshold <= value && value <= (thresholdMax || threshold));
            default:
                console.warn(`Unknown operator: ${operator}`);
                return false;
        }
    } catch (e) {
        console.error('Error evaluating condition:', e);
        return false;
    }
}

/**
 * Build adjacency map from edges for quick lookup.
 * 
 * @param {Array} edges - Array of edge objects with source and target
 * @returns {Object} Map of sourceId -> [targetIds]
 */
export function buildAdjacencyMap(edges) {
    const adjacency = {};

    for (const edge of edges) {
        const source = edge.source || '';
        const target = edge.target || '';

        if (!adjacency[source]) {
            adjacency[source] = [];
        }
        adjacency[source].push(target);
    }

    return adjacency;
}

/**
 * Get nodes connected to given node.
 * 
 * @param {string} nodeId - Source node ID
 * @param {Object} adjacency - Adjacency map
 * @param {Array} nodes - All nodes
 * @returns {Array} Connected nodes
 */
export function getConnectedNodes(nodeId, adjacency, nodes) {
    const connectedIds = adjacency[nodeId] || [];
    const nodesMap = Object.fromEntries(nodes.map(n => [n.id, n]));

    return connectedIds
        .filter(id => id in nodesMap)
        .map(id => nodesMap[id]);
}

/**
 * Generate test data that would trigger conditions.
 * 
 * @param {Array} nodes - Workflow nodes
 * @returns {Object} Mock sensor data
 */
export function generateMockSensorData(nodes) {
    const mockData = {};

    for (const node of nodes) {
        const config = node.data?.config || {};
        if (!config.sensor_type) continue;

        const equipmentId = config.equipment_id || node.id;
        const sensorType = config.sensor_type;
        const threshold = config.threshold || 50;
        const operator = config.operator || '>';

        // Generate value that sometimes triggers, sometimes doesn't
        let value;
        if (Math.random() > 0.5) {
            // Generate triggering value
            if (operator === '>' || operator === '>=') {
                value = threshold + Math.random() * 20 + 5;
            } else if (operator === '<' || operator === '<=') {
                value = threshold - Math.random() * 20 - 5;
            } else {
                value = threshold;
            }
        } else {
            // Generate non-triggering value
            if (operator === '>' || operator === '>=') {
                value = threshold - Math.random() * 20 - 5;
            } else {
                value = threshold + Math.random() * 20 + 5;
            }
        }

        mockData[`${equipmentId}.${sensorType}`] = Math.round(value * 100) / 100;
    }

    return mockData;
}

// Export the workflow engine object
const workflowEngine = {
    evaluateCondition,
    buildAdjacencyMap,
    getConnectedNodes,
    generateMockSensorData,
};

export default workflowEngine;
