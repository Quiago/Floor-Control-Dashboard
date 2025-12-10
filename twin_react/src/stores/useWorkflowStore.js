// src/stores/useWorkflowStore.js
// State management for the Workflow Builder

import { v4 as uuidv4 } from 'uuid';
import { create } from 'zustand';
import * as db from '../services/database';
import { getSensorsForType, loadEquipmentFromGLB } from '../utils/glbParser';

// Category definitions
const CATEGORY_DEFINITIONS = [
    { key: 'analyzer', name: 'Analyzers', icon: 'Scan', type: 'equipment', color: 'purple' },
    { key: 'robot', name: 'Robots', icon: 'Box', type: 'equipment', color: 'blue' },
    { key: 'centrifuge', name: 'Centrifuges', icon: 'CircleDot', type: 'equipment', color: 'cyan' },
    { key: 'storage', name: 'Storage', icon: 'Package', type: 'equipment', color: 'green' },
    { key: 'conveyor', name: 'Conveyors', icon: 'ArrowRight', type: 'equipment', color: 'yellow' },
    { key: 'whatsapp', name: 'WhatsApp', icon: 'MessageCircle', type: 'action', color: 'green' },
    { key: 'email', name: 'Email', icon: 'Mail', type: 'action', color: 'blue' },
    { key: 'alert', name: 'System Alert', icon: 'Bell', type: 'action', color: 'red' },
    { key: 'webhook', name: 'Webhook', icon: 'Globe', type: 'action', color: 'gray' },
];

const OPERATOR_OPTIONS = [
    { value: '>', label: '> Greater than' },
    { value: '<', label: '< Less than' },
    { value: '>=', label: '>= Greater or equal' },
    { value: '<=', label: '<= Less or equal' },
    { value: '==', label: '== Equal to' },
    { value: '!=', label: '!= Not equal' },
    { value: 'between', label: 'Between (range)' },
];

const SEVERITY_OPTIONS = [
    { value: 'info', label: 'Info', color: 'blue' },
    { value: 'warning', label: 'Warning', color: 'yellow' },
    { value: 'critical', label: 'Critical', color: 'red' },
];

const useWorkflowStore = create((set, get) => ({
    // === REACTFLOW STATE ===
    nodes: [],
    edges: [],

    // === DRAG AND DROP ===
    draggedType: '',
    draggedIsAction: false,

    // === UI STATE ===
    showEquipmentPanel: true,
    selectedNodeId: '',
    showConfigPanel: false,
    selectedNodeCategory: '',
    selectedNodeIsAction: false,

    // === WORKFLOW METADATA ===
    currentWorkflowId: '',
    currentWorkflowName: 'New Workflow',
    currentWorkflowStatus: 'draft',

    // === WORKFLOW LIST ===
    savedWorkflows: [],
    showWorkflowList: false,

    // === EQUIPMENT LIST ===
    availableEquipment: [],

    // === CONFIG FORM VALUES ===
    configSensorType: '',
    configOperator: '>',
    configThreshold: '50',
    configThresholdMax: '100',
    configSeverity: 'warning',
    configPhoneNumber: '',
    configEmail: '',
    configWebhookUrl: '',
    configMessageTemplate: '',
    configSpecificEquipmentId: '',

    // === TEST MODE ===
    testMode: false,
    testResults: [],

    // === COUNTER ===
    nodeCounter: 0,

    // === STATIC DATA ===
    categoryDefinitions: CATEGORY_DEFINITIONS,
    equipmentCategories: CATEGORY_DEFINITIONS.filter(c => c.type === 'equipment'),
    actionCategories: CATEGORY_DEFINITIONS.filter(c => c.type === 'action'),
    operatorOptions: OPERATOR_OPTIONS,
    severityOptions: SEVERITY_OPTIONS,

    // === COMPUTED ===
    get isDragging() {
        return get().draggedType !== '';
    },

    getSelectedNodeSensors: () => {
        const { selectedNodeId, nodes } = get();
        if (!selectedNodeId) return [];

        const node = nodes.find(n => n.id === selectedNodeId);
        if (!node) return [];

        const category = node.data?.category || '';
        return getSensorsForType(category);
    },

    // === ACTIONS ===

    loadEquipment: () => {
        const equipment = loadEquipmentFromGLB();
        set({ availableEquipment: equipment });
        get().loadWorkflowsList();
    },

    loadWorkflowsList: () => {
        const workflows = db.getAllWorkflows();
        set({
            savedWorkflows: workflows.map(w => ({
                id: w.id,
                name: w.name,
                status: w.status,
                updated_at: w.updated_at?.slice(0, 16).replace('T', ' ') || '',
            })),
        });
    },

    // === DRAG AND DROP ===

    startDrag: (itemKey, isAction) => {
        set({ draggedType: itemKey, draggedIsAction: isAction });
    },

    cancelDrag: () => {
        set({ draggedType: '', draggedIsAction: false });
    },

    handleDrop: (clientX, clientY) => {
        const { draggedType, draggedIsAction, nodeCounter, categoryDefinitions } = get();

        if (!draggedType) return;

        // Get canvas position
        const canvas = document.getElementById('workflow-canvas');
        const rect = canvas?.getBoundingClientRect() || { left: 200, top: 80 };

        const xPos = clientX - rect.left - 64;
        const yPos = clientY - rect.top - 64;

        const newCounter = nodeCounter + 1;
        const nodeId = `node_${newCounter}`;

        const catInfo = categoryDefinitions.find(c => c.key === draggedType);
        const label = catInfo ? `${catInfo.name}-${newCounter}` : draggedType;
        const color = catInfo?.color || 'gray';

        // Color mapping
        const bgColors = {
            equipment: {
                purple: '#581c87', blue: '#1e3a8a', cyan: '#164e63',
                green: '#14532d', yellow: '#713f12',
            },
            action: {
                green: '#166534', blue: '#1e40af', red: '#991b1b', gray: '#374151',
            },
        };

        const borderColors = {
            equipment: {
                purple: '#a855f7', blue: '#3b82f6', cyan: '#22d3ee',
                green: '#22c55e', yellow: '#eab308',
            },
            action: {
                green: '#22c55e', blue: '#3b82f6', red: '#ef4444', gray: '#6b7280',
            },
        };

        const colorSet = draggedIsAction ? 'action' : 'equipment';
        const bgColor = bgColors[colorSet][color] || '#1f2937';
        const borderColor = borderColors[colorSet][color] || '#6b7280';

        const newNode = {
            id: nodeId,
            type: 'default',
            position: { x: Math.max(0, xPos), y: Math.max(0, yPos) },
            data: {
                label,
                category: draggedType,
                is_action: draggedIsAction,
                configured: false,
                config: {},
            },
            style: {
                background: bgColor,
                color: 'white',
                border: `2px solid ${borderColor}`,
                borderRadius: '8px',
                padding: '10px 15px',
                fontSize: '12px',
                fontWeight: '500',
                minWidth: '120px',
                textAlign: 'center',
                cursor: 'pointer',
            },
            sourcePosition: 'right',
            targetPosition: 'left',
        };

        set(state => ({
            nodes: [...state.nodes, newNode],
            nodeCounter: newCounter,
            draggedType: '',
            draggedIsAction: false,
            selectedNodeId: nodeId,
            selectedNodeCategory: draggedType,
            selectedNodeIsAction: draggedIsAction,
            showConfigPanel: true,
        }));

        get().resetConfigForm();
    },

    // === REACTFLOW HANDLERS ===

    onConnect: (connection) => {
        if (!connection) return;

        const { source, target } = connection;
        if (!source || !target) return;

        const existing = get().edges.some(e => e.source === source && e.target === target);
        if (existing) return;

        const newEdge = {
            id: `edge_${source}_${target}`,
            source,
            target,
            type: 'smoothstep',
            animated: true,
            style: { stroke: '#3b82f6', strokeWidth: 2 },
        };

        set(state => ({ edges: [...state.edges, newEdge] }));
    },

    onNodesChange: (changes) => {
        if (!changes) return;

        set(state => {
            const nodesMap = new Map(state.nodes.map(n => [n.id, n]));

            for (const change of changes) {
                const { type, id } = change;

                if (type === 'position' && nodesMap.has(id)) {
                    const pos = change.position;
                    if (pos?.x !== undefined && pos?.y !== undefined) {
                        const node = nodesMap.get(id);
                        nodesMap.set(id, {
                            ...node,
                            position: { x: pos.x, y: pos.y },
                        });
                    }
                } else if (type === 'select' && nodesMap.has(id)) {
                    if (change.selected) {
                        const node = nodesMap.get(id);
                        // Update selection state outside the loop
                        setTimeout(() => {
                            set({
                                selectedNodeId: id,
                                selectedNodeCategory: node.data?.category || '',
                                selectedNodeIsAction: node.data?.is_action || false,
                                showConfigPanel: true,
                            });
                            get().loadNodeConfig(node);
                        }, 0);
                    }
                } else if (type === 'remove' && nodesMap.has(id)) {
                    nodesMap.delete(id);
                    // Update edges and selection outside
                    setTimeout(() => {
                        set(s => ({
                            edges: s.edges.filter(e => e.source !== id && e.target !== id),
                            selectedNodeId: s.selectedNodeId === id ? '' : s.selectedNodeId,
                            showConfigPanel: s.selectedNodeId === id ? false : s.showConfigPanel,
                        }));
                    }, 0);
                }
            }

            return { nodes: Array.from(nodesMap.values()) };
        });
    },

    onEdgesChange: (changes) => {
        if (!changes) return;

        set(state => {
            const edgesMap = new Map(state.edges.map(e => [e.id, e]));

            for (const change of changes) {
                if (change.type === 'remove' && edgesMap.has(change.id)) {
                    edgesMap.delete(change.id);
                }
            }

            return { edges: Array.from(edgesMap.values()) };
        });
    },

    // === NODE CONFIGURATION ===

    resetConfigForm: () => {
        set({
            configSensorType: '',
            configOperator: '>',
            configThreshold: '50',
            configThresholdMax: '100',
            configSeverity: 'warning',
            configPhoneNumber: '',
            configEmail: '',
            configWebhookUrl: '',
            configMessageTemplate: '',
            configSpecificEquipmentId: '',
        });
    },

    loadNodeConfig: (node) => {
        const config = node.data?.config || {};

        if (!Object.keys(config).length) {
            get().resetConfigForm();
            return;
        }

        set({
            configSensorType: config.sensor_type || '',
            configOperator: config.operator || '>',
            configThreshold: String(config.threshold || 50),
            configThresholdMax: String(config.threshold_max || 100),
            configSeverity: config.severity || 'warning',
            configPhoneNumber: config.phone_number || '',
            configEmail: config.email || '',
            configWebhookUrl: config.webhook_url || '',
            configMessageTemplate: config.message_template || '',
            configSpecificEquipmentId: config.specific_equipment_id || '',
        });
    },

    closeConfigPanel: () => {
        set({ showConfigPanel: false, selectedNodeId: '' });
    },

    setConfigValue: (key, value) => {
        set({ [key]: value });
    },

    saveNodeConfig: () => {
        const state = get();
        const { selectedNodeId, selectedNodeIsAction, nodes } = state;

        if (!selectedNodeId) return;

        let config;

        if (selectedNodeIsAction) {
            config = {
                severity: state.configSeverity,
                phone_number: state.configPhoneNumber,
                email: state.configEmail,
                webhook_url: state.configWebhookUrl,
                message_template: state.configMessageTemplate,
            };
        } else {
            config = {
                sensor_type: state.configSensorType,
                operator: state.configOperator,
                threshold: parseFloat(state.configThreshold) || 50,
                threshold_max: parseFloat(state.configThresholdMax) || 100,
                severity: state.configSeverity,
                specific_equipment_id: state.configSpecificEquipmentId,
                equipment_id: selectedNodeId,
            };
        }

        set({
            nodes: nodes.map(node => {
                if (node.id === selectedNodeId) {
                    return {
                        ...node,
                        data: {
                            ...node.data,
                            configured: true,
                            config,
                        },
                        style: {
                            ...node.style,
                            boxShadow: '0 0 10px rgba(34, 197, 94, 0.5)',
                        },
                    };
                }
                return node;
            }),
        });

        console.log(`Configuration saved for ${state.selectedNodeCategory}`);
    },

    // === WORKFLOW MANAGEMENT ===

    setWorkflowName: (name) => set({ currentWorkflowName: name }),

    newWorkflow: () => {
        set({
            nodes: [],
            edges: [],
            currentWorkflowId: '',
            currentWorkflowName: 'New Workflow',
            currentWorkflowStatus: 'draft',
            selectedNodeId: '',
            showConfigPanel: false,
            nodeCounter: 0,
        });
    },

    saveWorkflow: () => {
        const { nodes, currentWorkflowId, currentWorkflowName, currentWorkflowStatus, edges } = get();

        if (!nodes.length) {
            console.warn('Nothing to save - add nodes first');
            return false;
        }

        const workflowId = currentWorkflowId || uuidv4();

        const success = db.saveWorkflow(
            workflowId,
            currentWorkflowName,
            '',
            nodes,
            edges,
            currentWorkflowStatus
        );

        if (success) {
            set({ currentWorkflowId: workflowId });
            get().loadWorkflowsList();
            console.log(`Workflow '${currentWorkflowName}' saved!`);
        }

        return success;
    },

    toggleWorkflowList: () => {
        const { showWorkflowList } = get();
        if (!showWorkflowList) {
            get().loadWorkflowsList();
        }
        set({ showWorkflowList: !showWorkflowList });
    },

    loadWorkflow: (workflowId) => {
        const workflow = db.getWorkflow(workflowId);

        if (!workflow) return;

        // Find max node counter
        let maxCounter = 0;
        for (const node of workflow.nodes || []) {
            try {
                const num = parseInt(node.id.split('_')[1]);
                if (num > maxCounter) maxCounter = num;
            } catch (e) { }
        }

        set({
            nodes: workflow.nodes || [],
            edges: workflow.edges || [],
            currentWorkflowId: workflowId,
            currentWorkflowName: workflow.name || 'Loaded Workflow',
            currentWorkflowStatus: workflow.status || 'draft',
            nodeCounter: maxCounter,
            showWorkflowList: false,
        });

        console.log(`Loaded '${workflow.name}'`);
    },

    deleteWorkflow: (workflowId) => {
        db.deleteWorkflow(workflowId);

        if (workflowId === get().currentWorkflowId) {
            get().newWorkflow();
        }

        get().loadWorkflowsList();
        console.log('Workflow deleted');
    },

    activateWorkflow: () => {
        const { nodes } = get();

        if (!nodes.length) {
            console.warn('Add nodes before activating');
            return;
        }

        set({ currentWorkflowStatus: 'active' });
        get().saveWorkflow();
        console.log('Workflow activated!');
    },

    clearWorkflow: () => {
        set({
            nodes: [],
            edges: [],
            selectedNodeId: '',
            showConfigPanel: false,
            nodeCounter: 0,
        });
    },

    toggleEquipmentPanel: () => {
        set(state => ({ showEquipmentPanel: !state.showEquipmentPanel }));
    },
}));

export default useWorkflowStore;
