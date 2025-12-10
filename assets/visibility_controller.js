/**
 * Visibility Controller - Bypass Reflex rx.cond() to prevent React Hooks violations
 *
 * This module handles conditional visibility using pure JavaScript DOM manipulation
 * instead of Reflex's reactive system, preventing constant page reloads during simulation.
 */

(function() {
    console.log('[VisibilityController] Initializing...');

    // State tracking
    const state = {
        simulationRunning: false,
        isExpanded: false,
        menuMode: 'main',
        selectedEquipment: null,
        isAlertActive: false,
        sensorCount: 0,
        alertCount: 0,
        isThinking: false,
        awaitingApproval: false
    };

    // Initialize observers
    function initializeStateObservers() {
        // Observer for simulation state changes
        const simulationObserver = new MutationObserver(() => {
            updateSimulationVisibility();
        });

        // Observer for alert state changes
        const alertObserver = new MutationObserver(() => {
            updateAlertVisibility();
        });

        // Start observing state bridge elements
        const stateBridge = document.getElementById('state-bridge');
        if (stateBridge) {
            simulationObserver.observe(stateBridge, {
                attributes: true,
                attributeFilter: ['data-simulation-running', 'data-sensor-count', 'data-alert-count']
            });
        }

        console.log('[VisibilityController] Observers initialized');
    }

    // Update visibility for simulation-related components
    function updateSimulationVisibility() {
        const stateBridge = document.getElementById('state-bridge');
        if (!stateBridge) return;

        const isRunning = stateBridge.getAttribute('data-simulation-running') === 'true';
        const sensorCount = parseInt(stateBridge.getAttribute('data-sensor-count') || '0');
        const alertCount = parseInt(stateBridge.getAttribute('data-alert-count') || '0');

        // Update state
        state.simulationRunning = isRunning;
        state.sensorCount = sensorCount;
        state.alertCount = alertCount;

        // Toggle simulation badge
        const simBadge = document.getElementById('sim-status-active');
        const monitorBadge = document.getElementById('sim-status-monitoring');
        if (simBadge) simBadge.classList.toggle('hidden', !isRunning);
        if (monitorBadge) monitorBadge.classList.toggle('hidden', isRunning);

        // Toggle live sensor dashboard
        const sensorDashboard = document.getElementById('live-sensor-dashboard');
        if (sensorDashboard) {
            sensorDashboard.classList.toggle('hidden', !isRunning);
        }

        // Toggle sensor values container
        const sensorContainer = document.getElementById('sensor-values-container');
        const sensorLoading = document.getElementById('sensor-loading-state');
        if (sensorContainer) {
            sensorContainer.classList.toggle('hidden', sensorCount === 0);
        }
        if (sensorLoading) {
            sensorLoading.classList.toggle('hidden', sensorCount > 0);
        }

        // Toggle alert list vs empty state
        const alertList = document.getElementById('alert-stream');
        const alertEmpty = document.getElementById('alert-empty-state');
        if (alertList) {
            alertList.classList.toggle('hidden', alertCount === 0);
        }
        if (alertEmpty) {
            alertEmpty.classList.toggle('hidden', alertCount > 0);
        }

        // Toggle simulation stop button
        const stopButton = document.getElementById('sim-stop-button');
        if (stopButton) {
            stopButton.classList.toggle('hidden', !isRunning);
        }

        console.log('[VisibilityController] Simulation visibility updated:', {
            isRunning,
            sensorCount,
            alertCount
        });
    }

    // Update visibility for alert indicator
    function updateAlertVisibility() {
        const stateBridge = document.getElementById('state-bridge');
        if (!stateBridge) return;

        const isAlertActive = stateBridge.getAttribute('data-alert-active') === 'true';
        state.isAlertActive = isAlertActive;

        const alertIndicator = document.getElementById('alert-indicator');
        if (alertIndicator) {
            alertIndicator.classList.toggle('hidden', !isAlertActive);
        }

        console.log('[VisibilityController] Alert visibility updated:', isAlertActive);
    }

    // Update visibility for knowledge graph panel
    function updateKnowledgeGraphVisibility() {
        const stateBridge = document.getElementById('state-bridge');
        if (!stateBridge) return;

        const isExpanded = stateBridge.getAttribute('data-is-expanded') === 'true';
        state.isExpanded = isExpanded;

        const kgPanel = document.getElementById('knowledge-graph-panel');
        if (kgPanel) {
            kgPanel.classList.toggle('hidden', !isExpanded);
        }

        console.log('[VisibilityController] Knowledge graph visibility updated:', isExpanded);
    }

    // Update visibility for context menu
    function updateContextMenuVisibility() {
        const stateBridge = document.getElementById('state-bridge');
        if (!stateBridge) return;

        const selectedEquipment = stateBridge.getAttribute('data-selected-equipment');
        const menuMode = stateBridge.getAttribute('data-menu-mode') || 'main';

        state.selectedEquipment = selectedEquipment;
        state.menuMode = menuMode;

        const contextMenu = document.getElementById('floating-context-menu');
        if (contextMenu) {
            contextMenu.classList.toggle('hidden', !selectedEquipment);
        }

        const propsView = document.getElementById('context-menu-properties');
        const actionsView = document.getElementById('context-menu-actions');
        if (propsView) {
            propsView.classList.toggle('hidden', menuMode !== 'main');
        }
        if (actionsView) {
            actionsView.classList.toggle('hidden', menuMode === 'main');
        }

        console.log('[VisibilityController] Context menu visibility updated:', {
            selectedEquipment,
            menuMode
        });
    }

    // Update visibility for chat panel states
    function updateChatPanelVisibility() {
        const stateBridge = document.getElementById('state-bridge');
        if (!stateBridge) return;

        const isThinking = stateBridge.getAttribute('data-is-thinking') === 'true';
        const awaitingApproval = stateBridge.getAttribute('data-awaiting-approval') === 'true';

        state.isThinking = isThinking;
        state.awaitingApproval = awaitingApproval;

        const thinkingIndicator = document.getElementById('thinking-indicator');
        const approvalButtons = document.getElementById('approval-buttons');

        if (thinkingIndicator) {
            thinkingIndicator.classList.toggle('hidden', !isThinking);
        }
        if (approvalButtons) {
            approvalButtons.classList.toggle('hidden', !awaitingApproval);
        }

        console.log('[VisibilityController] Chat panel visibility updated:', {
            isThinking,
            awaitingApproval
        });
    }

    // Update visibility for controls hint
    function updateControlsHintVisibility() {
        const stateBridge = document.getElementById('state-bridge');
        if (!stateBridge) return;

        const isExpanded = stateBridge.getAttribute('data-is-expanded') === 'true';
        const controlsHint = document.getElementById('controls-hint');

        if (controlsHint) {
            controlsHint.classList.toggle('hidden', isExpanded);
        }
    }

    // Listen for state change events from Python
    window.addEventListener('nexusStateChange', function(e) {
        const { type, value } = e.detail;
        console.log('[VisibilityController] State change event:', type, value);

        // Update state bridge data attributes
        const stateBridge = document.getElementById('state-bridge');
        if (!stateBridge) {
            console.error('[VisibilityController] State bridge not found');
            return;
        }

        switch(type) {
            case 'simulation':
                stateBridge.setAttribute('data-simulation-running', value.running);
                stateBridge.setAttribute('data-sensor-count', value.sensorCount || 0);
                stateBridge.setAttribute('data-alert-count', value.alertCount || 0);
                updateSimulationVisibility();
                break;
            case 'alert':
                stateBridge.setAttribute('data-alert-active', value);
                updateAlertVisibility();
                break;
            case 'knowledge-graph':
                stateBridge.setAttribute('data-is-expanded', value);
                updateKnowledgeGraphVisibility();
                updateControlsHintVisibility();
                break;
            case 'context-menu':
                stateBridge.setAttribute('data-selected-equipment', value.equipment || '');
                stateBridge.setAttribute('data-menu-mode', value.mode || 'main');
                updateContextMenuVisibility();
                break;
            case 'chat':
                stateBridge.setAttribute('data-is-thinking', value.thinking || false);
                stateBridge.setAttribute('data-awaiting-approval', value.approval || false);
                updateChatPanelVisibility();
                break;
        }
    });

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initializeStateObservers();
            updateSimulationVisibility();
            console.log('[VisibilityController] Ready');
        });
    } else {
        initializeStateObservers();
        updateSimulationVisibility();
        console.log('[VisibilityController] Ready');
    }

    // Expose API for manual updates
    window.NexusVisibility = {
        updateSimulation: updateSimulationVisibility,
        updateAlert: updateAlertVisibility,
        updateKnowledgeGraph: updateKnowledgeGraphVisibility,
        updateContextMenu: updateContextMenuVisibility,
        updateChatPanel: updateChatPanelVisibility,
        getState: () => ({ ...state })
    };

    console.log('[VisibilityController] Loaded successfully');
})();
