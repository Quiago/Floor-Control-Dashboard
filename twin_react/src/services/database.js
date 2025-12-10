// src/services/database.js
// LocalStorage-based database service for workflow persistence

const STORAGE_KEYS = {
    WORKFLOWS: 'nexus_workflows',
    ALERTS: 'nexus_alerts',
    EXECUTIONS: 'nexus_executions',
    SENSOR_READINGS: 'nexus_sensor_readings',
};

// Helper to get data from localStorage
function getStorageData(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : [];
    } catch (e) {
        console.error(`Error reading ${key} from localStorage:`, e);
        return [];
    }
}

// Helper to set data to localStorage
function setStorageData(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
        return true;
    } catch (e) {
        console.error(`Error writing ${key} to localStorage:`, e);
        return false;
    }
}

// === WORKFLOW CRUD ===

export function saveWorkflow(workflowId, name, description, nodes, edges, status = 'draft') {
    const workflows = getStorageData(STORAGE_KEYS.WORKFLOWS);
    const now = new Date().toISOString();

    const existingIndex = workflows.findIndex(w => w.id === workflowId);

    const workflowData = {
        id: workflowId,
        name,
        description,
        nodes,
        edges,
        status,
        created_at: existingIndex >= 0 ? workflows[existingIndex].created_at : now,
        updated_at: now,
    };

    if (existingIndex >= 0) {
        workflows[existingIndex] = workflowData;
    } else {
        workflows.push(workflowData);
    }

    return setStorageData(STORAGE_KEYS.WORKFLOWS, workflows);
}

export function getWorkflow(workflowId) {
    const workflows = getStorageData(STORAGE_KEYS.WORKFLOWS);
    return workflows.find(w => w.id === workflowId) || null;
}

export function getAllWorkflows(status = null) {
    const workflows = getStorageData(STORAGE_KEYS.WORKFLOWS);
    const filtered = status
        ? workflows.filter(w => w.status === status)
        : workflows;

    // Sort by updated_at descending
    return filtered.sort((a, b) =>
        new Date(b.updated_at) - new Date(a.updated_at)
    );
}

export function deleteWorkflow(workflowId) {
    const workflows = getStorageData(STORAGE_KEYS.WORKFLOWS);
    const filtered = workflows.filter(w => w.id !== workflowId);
    return setStorageData(STORAGE_KEYS.WORKFLOWS, filtered);
}

export function updateWorkflowStatus(workflowId, status) {
    const workflows = getStorageData(STORAGE_KEYS.WORKFLOWS);
    const index = workflows.findIndex(w => w.id === workflowId);

    if (index >= 0) {
        workflows[index].status = status;
        workflows[index].updated_at = new Date().toISOString();
        return setStorageData(STORAGE_KEYS.WORKFLOWS, workflows);
    }
    return false;
}

// === ALERT LOGS ===

export function logAlert(workflowId, actionType, recipient, message, status = 'pending', errorMessage = null) {
    const alerts = getStorageData(STORAGE_KEYS.ALERTS);

    const alertData = {
        id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        workflow_id: workflowId,
        action_type: actionType,
        recipient,
        message,
        status,
        error_message: errorMessage,
        created_at: new Date().toISOString(),
    };

    // Keep only last 1000 alerts
    alerts.unshift(alertData);
    if (alerts.length > 1000) {
        alerts.splice(1000);
    }

    setStorageData(STORAGE_KEYS.ALERTS, alerts);
    return alertData.id;
}

export function getRecentAlerts(limit = 100, actionType = null) {
    const alerts = getStorageData(STORAGE_KEYS.ALERTS);

    const filtered = actionType
        ? alerts.filter(a => a.action_type === actionType)
        : alerts;

    return filtered.slice(0, limit);
}

export function updateAlertStatus(alertId, status, errorMessage = null) {
    const alerts = getStorageData(STORAGE_KEYS.ALERTS);
    const index = alerts.findIndex(a => a.id === alertId);

    if (index >= 0) {
        alerts[index].status = status;
        if (errorMessage) {
            alerts[index].error_message = errorMessage;
        }
        return setStorageData(STORAGE_KEYS.ALERTS, alerts);
    }
    return false;
}

// === EXECUTION LOGS ===

export function logExecutionStart(workflowId, triggeredBy, triggerData) {
    const executions = getStorageData(STORAGE_KEYS.EXECUTIONS);

    const execution = {
        id: `exec_${Date.now()}`,
        workflow_id: workflowId,
        triggered_by: triggeredBy,
        trigger_data: triggerData,
        status: 'running',
        result: null,
        started_at: new Date().toISOString(),
        completed_at: null,
    };

    executions.unshift(execution);
    if (executions.length > 500) {
        executions.splice(500);
    }

    setStorageData(STORAGE_KEYS.EXECUTIONS, executions);
    return execution.id;
}

export function logExecutionComplete(executionId, status, result) {
    const executions = getStorageData(STORAGE_KEYS.EXECUTIONS);
    const index = executions.findIndex(e => e.id === executionId);

    if (index >= 0) {
        executions[index].status = status;
        executions[index].result = result;
        executions[index].completed_at = new Date().toISOString();
        return setStorageData(STORAGE_KEYS.EXECUTIONS, executions);
    }
    return false;
}

export function getRecentExecutions(limit = 50, workflowId = null) {
    const executions = getStorageData(STORAGE_KEYS.EXECUTIONS);

    const filtered = workflowId
        ? executions.filter(e => e.workflow_id === workflowId)
        : executions;

    return filtered.slice(0, limit);
}

// === SENSOR DATA ===

export function logSensorReading(equipmentId, sensorType, value, unit) {
    const readings = getStorageData(STORAGE_KEYS.SENSOR_READINGS);

    readings.unshift({
        equipment_id: equipmentId,
        sensor_type: sensorType,
        value,
        unit,
        timestamp: new Date().toISOString(),
    });

    // Keep only last 10000 readings
    if (readings.length > 10000) {
        readings.splice(10000);
    }

    setStorageData(STORAGE_KEYS.SENSOR_READINGS, readings);
}

export function getLatestSensorReading(equipmentId, sensorType) {
    const readings = getStorageData(STORAGE_KEYS.SENSOR_READINGS);

    return readings.find(r =>
        r.equipment_id === equipmentId && r.sensor_type === sensorType
    ) || null;
}

// Export all as default object for convenience
const db = {
    saveWorkflow,
    getWorkflow,
    getAllWorkflows,
    deleteWorkflow,
    updateWorkflowStatus,
    logAlert,
    getRecentAlerts,
    updateAlertStatus,
    logExecutionStart,
    logExecutionComplete,
    getRecentExecutions,
    logSensorReading,
    getLatestSensorReading,
};

export default db;
