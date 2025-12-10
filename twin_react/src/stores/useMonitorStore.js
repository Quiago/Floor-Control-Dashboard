// src/stores/useMonitorStore.js
// State management for the Monitor page

import { create } from 'zustand';

const useMonitorStore = create((set, get) => ({
    // === 3D SELECTION ===
    selectedObjectName: '',
    menuMode: 'main', // main, actions
    isExpanded: false,
    isAlertActive: false,

    // === JS COMMANDS (for model-viewer) ===
    jsCommand: '',

    // === EQUIPMENT PROPERTIES ===
    equipmentTemp: 0,
    equipmentPressure: 0,
    equipmentStatus: 'Unknown',
    equipmentRul: 0,
    equipmentLine: '',
    equipmentSensors: [],
    equipmentDependsOn: [],
    equipmentAffects: [],
    equipmentProduct: '',

    // === ACTIONS ===

    handle3DSelection: (objectName) => {
        if (!objectName) {
            set({
                selectedObjectName: '',
                menuMode: 'main',
                isExpanded: false,
                jsCommand: 'restore',
            });
            return;
        }

        // Simulate knowledge graph query with random data
        const rul = Math.floor(Math.random() * 58) + 40;
        const statuses = ['Optimal', 'Warning', 'Critical'];
        const lines = ['Alpha', 'Beta', 'Gamma'];
        const products = ['Vaccine Batch #99', 'Serum Vials 50ml', 'Antibiotic Strips'];

        set({
            selectedObjectName: objectName,
            menuMode: 'main',
            equipmentTemp: Math.round((Math.random() * 40 + 45) * 10) / 10,
            equipmentPressure: Math.round((Math.random() * 150 + 100) * 10) / 10,
            equipmentStatus: statuses[Math.floor(Math.random() * 3)],
            equipmentRul: rul,
            equipmentLine: `Line-${lines[Math.floor(Math.random() * 3)]}`,
            equipmentSensors: [
                `Vib-Sens-${Math.floor(Math.random() * 900) + 100}`,
                'Therm-Coupler-A',
                'Flow-Meter-X',
            ],
            equipmentDependsOn: [
                `Feeder-${Math.floor(Math.random() * 5) + 1}`,
                'Power-Unit-Main',
            ],
            equipmentAffects: [
                `Packager-${Math.floor(Math.random() * 10) + 10}`,
                'Quality-Gate-B',
            ],
            equipmentProduct: products[Math.floor(Math.random() * 3)],
        });
    },

    clearSelection: () => {
        set({
            selectedObjectName: '',
            menuMode: 'main',
            isExpanded: false,
            jsCommand: 'restore',
        });
    },

    setMenuMode: (mode) => set({ menuMode: mode }),

    toggleExpand: () => {
        const { isExpanded, selectedObjectName } = get();
        const newExpanded = !isExpanded;

        set({
            isExpanded: newExpanded,
            jsCommand: newExpanded
                ? `isolate:${selectedObjectName}`
                : 'restore',
        });
    },

    setJsCommand: (command) => set({ jsCommand: command }),

    handleQuickAction: (action) => {
        const { selectedObjectName } = get();
        console.log(`Executing '${action}' on ${selectedObjectName}`);

        if (action === 'STOP') {
            set({ equipmentStatus: 'Critical' });
        }
    },

    setAlertActive: (active) => set({ isAlertActive: active }),
}));

export default useMonitorStore;
