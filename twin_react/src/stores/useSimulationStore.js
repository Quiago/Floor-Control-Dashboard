// src/stores/useSimulationStore.js
// State management for simulation functionality

import { create } from 'zustand';
import { logAlert } from '../services/database';
import { createThresholdAlert, sendEmail, sendWebhook, sendWhatsApp } from '../services/notificationService';
import { generateSensorData } from '../services/sensorSimulator';
import { buildAdjacencyMap, evaluateCondition } from '../services/workflowEngine';

const useSimulationStore = create((set, get) => ({
    // === SIMULATION CONTROL ===
    simulationRunning: false,
    simulationSpeed: 2, // seconds between ticks
    simulationTickCount: 0,

    // === SENSOR DATA ===
    currentSensorValues: [],

    // === ALERTS ===
    alertFeed: [],
    latestAlertEquipment: '',
    showAlertFeed: true,

    // === TOAST ===
    toastMessage: '',
    toastType: 'info',
    showToast: false,

    // === CACHED WORKFLOW DATA ===
    cachedNodes: [],
    cachedEdges: [],

    // === ACTIONS ===

    setSimulationSpeed: (speed) => {
        set({ simulationSpeed: parseInt(speed) || 2 });
    },

    startSimulation: (nodes, edges) => {
        const { simulationRunning } = get();

        if (simulationRunning) {
            console.log('[Simulation] Already running');
            return false;
        }

        // Validate workflow
        let hasConfiguredEquipment = false;
        let hasConnectedAction = false;

        for (const node of nodes) {
            if (!node.data?.is_action && node.data?.configured) {
                hasConfiguredEquipment = true;
                for (const edge of edges) {
                    if (edge.source === node.id) {
                        hasConnectedAction = true;
                        break;
                    }
                }
            }
        }

        if (!hasConfiguredEquipment) {
            get().showToastMessage('Configure at least one equipment node first', 'warning');
            return false;
        }

        if (!hasConnectedAction) {
            get().showToastMessage('Connect equipment to an action node first', 'warning');
            return false;
        }

        set({
            cachedNodes: nodes,
            cachedEdges: edges,
            simulationTickCount: 0,
            simulationRunning: true,
        });

        get().showToastMessage(`🚀 Simulation started! Updates every ${get().simulationSpeed}s`, 'success');
        return true;
    },

    stopSimulation: () => {
        set({
            simulationRunning: false,
            currentSensorValues: [],
            latestAlertEquipment: '',
        });
        get().showToastMessage('Simulation stopped', 'info');
    },

    simulationTick: async () => {
        const { simulationRunning, cachedNodes, cachedEdges, simulationTickCount } = get();

        if (!simulationRunning || !cachedNodes.length) {
            return;
        }

        const newTick = simulationTickCount + 1;

        // Generate sensor data
        const { dataDict, dataList } = generateSensorData(cachedNodes, newTick);

        set({
            simulationTickCount: newTick,
            currentSensorValues: dataList,
        });

        console.log(`[Simulation] Tick ${newTick}: ${dataList.length} sensors`);

        // Evaluate workflow and trigger actions
        await get().evaluateAndTrigger(dataDict, newTick);
    },

    evaluateAndTrigger: async (sensorData, tick) => {
        const { cachedNodes, cachedEdges } = get();

        const adjacency = buildAdjacencyMap(cachedEdges);
        const nodesMap = Object.fromEntries(cachedNodes.map(n => [n.id, n]));

        for (const node of cachedNodes) {
            if (node.data?.is_action) continue;

            const config = node.data?.config || {};
            if (!config.sensor_type) continue;

            const equipmentId = config.equipment_id || node.id;
            const sensorType = config.sensor_type;
            const operator = config.operator || '>';
            const threshold = parseFloat(config.threshold || 0);

            const sensorKey = `${equipmentId}.${sensorType}`;
            const currentValue = sensorData[sensorKey];

            if (currentValue === undefined) continue;

            const triggered = evaluateCondition(currentValue, operator, threshold);

            if (triggered) {
                const specificId = config.specific_equipment_id;
                if (specificId) {
                    set({ latestAlertEquipment: specificId });
                }

                const connectedIds = adjacency[node.id] || [];

                for (const actionId of connectedIds) {
                    const actionNode = nodesMap[actionId];
                    if (actionNode) {
                        await get().executeAction(node, actionNode, currentValue, threshold, sensorType);
                    }
                }
            }
        }
    },

    executeAction: async (triggerNode, actionNode, value, threshold, sensorType) => {
        const actionConfig = actionNode.data?.config || {};
        const actionType = actionNode.data?.category || '';
        const equipmentName = triggerNode.data?.label || 'Equipment';
        const severity = actionConfig.severity || 'warning';

        const alertContent = createThresholdAlert({
            equipmentName,
            sensor: sensorType,
            value,
            threshold,
            unit: actionConfig.unit || '',
            severity,
        });

        let result = null;
        let recipient = '';

        switch (actionType) {
            case 'whatsapp':
                recipient = actionConfig.phone_number || '';
                if (recipient) {
                    result = await sendWhatsApp(recipient, alertContent.text);
                    console.log(`[WHATSAPP] Sent to ${recipient}`);
                }
                break;

            case 'email':
                recipient = actionConfig.email || '';
                if (recipient) {
                    result = await sendEmail(recipient, alertContent.subject, alertContent.text);
                    console.log(`[EMAIL] Sent to ${recipient}`);
                }
                break;

            case 'alert':
                recipient = 'system';
                result = { success: true, message_id: 'system' };
                console.log(`[SYSTEM ALERT] ${alertContent.subject}`);
                break;

            case 'webhook':
                recipient = actionConfig.webhook_url || '';
                if (recipient) {
                    result = await sendWebhook(recipient, {
                        equipment: equipmentName,
                        sensor: sensorType,
                        value,
                        threshold,
                        severity,
                        timestamp: new Date().toISOString(),
                    });
                    console.log(`[WEBHOOK] Sent to ${recipient}`);
                }
                break;
        }

        // Add to alert feed
        const alertEntry = {
            id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            timestamp: new Date().toLocaleTimeString(),
            equipment: equipmentName,
            sensor: sensorType,
            value,
            threshold,
            action_type: actionType,
            recipient,
            severity,
            success: result?.success || false,
        };

        set(state => ({
            alertFeed: [alertEntry, ...state.alertFeed.slice(0, 19)],
        }));

        // Show toast
        const emoji = severity === 'critical' ? '🔴' : '🟡';
        get().showToastMessage(
            `${emoji} ALERT: ${equipmentName} ${sensorType}=${value} (>${threshold})`,
            severity === 'critical' ? 'error' : 'warning'
        );

        // Log to database
        logAlert('', actionType, recipient, alertContent.text, result?.success ? 'sent' : 'failed');
    },

    toggleAlertFeed: () => {
        set(state => ({ showAlertFeed: !state.showAlertFeed }));
    },

    clearAlertFeed: () => {
        set({ alertFeed: [], latestAlertEquipment: '' });
    },

    showToastMessage: (message, type = 'info') => {
        set({
            toastMessage: message,
            toastType: type,
            showToast: true,
        });

        // Auto-hide after 4 seconds
        setTimeout(() => {
            set({ showToast: false });
        }, 4000);
    },

    hideToast: () => {
        set({ showToast: false });
    },
}));

export default useSimulationStore;
