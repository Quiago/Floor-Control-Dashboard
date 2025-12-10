# app/states/simulation_state.py
"""
Isolated Simulation State - Changes here don't affect workflow UI.

This state handles all simulation-related functionality:
- Simulation running/speed/tick
- Sensor data generation
- Alert feed
- Workflow evaluation and action execution
"""
import reflex as rx
from typing import List, Dict, Any
import random
import math
from datetime import datetime


class SimulationState(rx.State):
    """Isolated simulation state to prevent UI re-renders."""

    # === SIMULATION CONTROL ===
    simulation_running: bool = False
    simulation_speed: int = 2  # seconds between ticks
    simulation_tick_count: int = 0

    # === SENSOR DATA ===
    current_sensor_values: List[Dict] = []

    # === ALERTS ===
    alert_feed: List[Dict] = []
    latest_alert_equipment: str = ""
    show_alert_feed: bool = True

    # === TOAST ===
    toast_message: str = ""
    toast_type: str = "info"
    show_toast: bool = False

    # === CACHED WORKFLOW DATA ===
    _cached_nodes: List[Dict] = []
    _cached_edges: List[Dict] = []
    
    # === WORKFLOW REFERENCE ===
    # We need to get workflow data from WorkflowState for evaluation
    # This is done via lazy import to avoid circular dependencies
    
    def _get_workflow_state(self):
        """Get WorkflowState for accessing workflow nodes/edges."""
        from app.states.workflow_state import WorkflowState
        return WorkflowState
    
    def _get_workflow_data(self):
        """Get current workflow nodes and edges."""
        # Access the parent state's workflow data
        from reflex.state import BaseState
        ws = self._get_workflow_state()
        # Return nodes/edges from WorkflowState
        # Note: In Reflex, we access other state via the router substates
        return {
            'nodes': getattr(self, '_cached_nodes', []),
            'edges': getattr(self, '_cached_edges', [])
        }
    
    # === EVENTS ===
    
    @rx.event
    def toggle_alert_feed(self):
        """Toggle alert feed visibility."""
        self.show_alert_feed = not self.show_alert_feed
    
    @rx.event
    def clear_alert_feed(self):
        """Clear the alert feed."""
        self.alert_feed = []
        self.latest_alert_equipment = ""
    
    @rx.event
    def set_simulation_speed(self, speed: str):
        """Set simulation speed (seconds between ticks)."""
        try:
            self.simulation_speed = int(speed)
        except ValueError:
            pass
    
    @rx.event
    def start_simulation(self, nodes: List[Dict], edges: List[Dict]):
        """Start the simulation with workflow data."""
        if self.simulation_running:
            return
        
        # Validate workflow
        has_configured_equipment = False
        has_connected_action = False
        
        for node in nodes:
            if not node.get('data', {}).get('is_action', False):
                if node.get('data', {}).get('configured', False):
                    has_configured_equipment = True
                    for edge in edges:
                        if edge.get('source') == node['id']:
                            has_connected_action = True
                            break
        
        if not has_configured_equipment:
            self._show_toast("Configure at least one equipment node first", "warning")
            return
        
        if not has_connected_action:
            self._show_toast("Connect equipment to an action node first", "warning")
            return
        
        # Cache workflow data for tick processing
        self._cached_nodes = nodes
        self._cached_edges = edges
        
        self.simulation_tick_count = 0
        self.simulation_running = True
        self._show_toast(f"🚀 Simulation started! Updates every {self.simulation_speed}s", "success")
    
    @rx.event
    def stop_simulation(self):
        """Stop the simulation."""
        self.simulation_running = False
        self.current_sensor_values = []
        self.latest_alert_equipment = ""
        self._show_toast("Simulation stopped", "info")
    
    @rx.event
    async def simulation_tick(self):
        """Process one simulation tick - called by JavaScript interval."""
        if not self.simulation_running:
            return
        
        nodes = getattr(self, '_cached_nodes', [])
        edges = getattr(self, '_cached_edges', [])
        
        if not nodes:
            return
        
        self.simulation_tick_count += 1
        tick = self.simulation_tick_count
        
        # Generate sensor data
        sensor_data_dict, sensor_data_list = self._generate_sensor_data(nodes, tick)
        self.current_sensor_values = sensor_data_list
        
        print(f"[Simulation] Tick {tick}: {len(sensor_data_list)} sensors")
        
        # Evaluate workflow and trigger actions
        await self._evaluate_and_trigger(nodes, edges, sensor_data_dict, tick)
    
    def _generate_sensor_data(self, nodes: List[Dict], tick: int):
        """Generate simulated sensor data based on configured nodes."""
        data_dict = {}
        data_list = []
        
        for node in nodes:
            if node.get('data', {}).get('is_action', False):
                continue
            
            config = node.get('data', {}).get('config', {})
            if not config:
                continue
            
            equipment_id = config.get('equipment_id', node['id'])
            sensor_type = config.get('sensor_type', '')
            threshold = float(config.get('threshold', 50))
            
            if not sensor_type:
                continue
            
            sensor_key = f"{equipment_id}.{sensor_type}"
            
            # Generate value that oscillates around 80% of threshold
            base_value = threshold * 0.8
            noise = random.uniform(-threshold * 0.1, threshold * 0.1)
            oscillation = math.sin(tick * 0.3) * threshold * 0.15
            
            value = base_value + noise + oscillation
            
            # Every 8 ticks, create a spike that exceeds threshold
            if tick % 8 == 0:
                value = threshold * random.uniform(1.1, 1.3)
            
            value = round(value, 2)
            data_dict[sensor_key] = value
            
            # Pre-compute display values
            is_alert = value > threshold
            progress_pct = min(100, int((value / threshold) * 100)) if threshold > 0 else 0
            status = 'alert' if is_alert else ('warning' if progress_pct > 80 else 'normal')
            
            data_list.append({
                'key': sensor_type,
                'value': value,
                'threshold': threshold,
                'equipment': node.get('data', {}).get('label', equipment_id),
                'is_alert': is_alert,
                'progress_pct': progress_pct,
                'status': status
            })
        
        return data_dict, data_list
    
    async def _evaluate_and_trigger(self, nodes: List[Dict], edges: List[Dict], 
                                     sensor_data: Dict[str, float], tick: int):
        """Evaluate workflow conditions and trigger actions if needed."""
        from app.services.workflow_engine import workflow_engine
        
        # Build adjacency map
        adjacency = {}
        for edge in edges:
            source = edge.get('source', '')
            target = edge.get('target', '')
            if source not in adjacency:
                adjacency[source] = []
            adjacency[source].append(target)
        
        nodes_map = {n['id']: n for n in nodes}
        
        for node in nodes:
            if node.get('data', {}).get('is_action', False):
                continue
            
            config = node.get('data', {}).get('config', {})
            if not config or not config.get('sensor_type'):
                continue
            
            equipment_id = config.get('equipment_id', node['id'])
            sensor_type = config.get('sensor_type')
            operator = config.get('operator', '>')
            threshold = float(config.get('threshold', 0))
            
            sensor_key = f"{equipment_id}.{sensor_type}"
            current_value = sensor_data.get(sensor_key)
            
            if current_value is None:
                continue
            
            triggered = workflow_engine.evaluate_condition(
                current_value, operator, threshold
            )
            
            if triggered:
                specific_id = node['data'].get('config', {}).get('specific_equipment_id')
                if specific_id:
                    self.latest_alert_equipment = specific_id
                    # Update MonitorState mirror for 3D visual alerts
                    await self._update_monitor_alert(specific_id)

                connected_ids = adjacency.get(node['id'], [])

                for action_id in connected_ids:
                    action_node = nodes_map.get(action_id)
                    if action_node:
                        await self._execute_action(
                            node, action_node, current_value, threshold, sensor_type
                        )
    
    async def _update_monitor_alert(self, equipment_id: str):
        """Update MonitorState with the latest alert for 3D visualization."""
        try:
            from app.states.monitor_state import MonitorState
            monitor_state = await self.get_state(MonitorState)
            monitor_state.alert_equipment_mirror = equipment_id
        except Exception as e:
            print(f"[SimulationState] Error updating monitor alert: {e}")

    async def _execute_action(self, trigger_node: Dict, action_node: Dict,
                             value: float, threshold: float, sensor_type: str):
        """Execute an action node (send notification)."""
        from app.services.notification_service import notification_service, AlertTemplates
        
        action_config = action_node.get('data', {}).get('config', {})
        action_type = action_node.get('data', {}).get('category', '')
        equipment_name = trigger_node.get('data', {}).get('label', 'Equipment')
        severity = action_config.get('severity', 'warning')
        
        alert_content = AlertTemplates.threshold_alert(
            equipment_name=equipment_name,
            sensor=sensor_type,
            value=value,
            threshold=threshold,
            unit=action_config.get('unit', ''),
            severity=severity
        )
        
        result = None
        recipient = ""
        
        if action_type == 'whatsapp':
            recipient = action_config.get('phone_number', '')
            if recipient:
                result = await notification_service.send_whatsapp(
                    recipient, alert_content['text']
                )
                print(f"[WHATSAPP] Sent to {recipient}: {alert_content['subject']}")
        
        elif action_type == 'email':
            recipient = action_config.get('email', '')
            if recipient:
                result = await notification_service.send_email(
                    recipient,
                    alert_content['subject'],
                    alert_content['text'],
                    html_body=alert_content.get('html')
                )
                print(f"[EMAIL] Sent to {recipient}: {alert_content['subject']}")
        
        elif action_type == 'alert':
            recipient = 'system'
            result = type('Result', (), {'success': True, 'message_id': 'system'})()
            print(f"[SYSTEM ALERT] {alert_content['subject']}")
        
        elif action_type == 'webhook':
            recipient = action_config.get('webhook_url', '')
            if recipient:
                result = await notification_service.send_webhook(
                    recipient,
                    {
                        'equipment': equipment_name,
                        'sensor': sensor_type,
                        'value': value,
                        'threshold': threshold,
                        'severity': severity,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                print(f"[WEBHOOK] Sent to {recipient}")
        
        # Add to alert feed
        alert_entry = {
            'id': f"alert_{datetime.now().timestamp()}",
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'equipment': equipment_name,
            'sensor': sensor_type,
            'value': value,
            'threshold': threshold,
            'action_type': action_type,
            'recipient': recipient,
            'severity': severity,
            'success': result.success if result else False
        }
        
        self.alert_feed = [alert_entry, *self.alert_feed[:19]]
        
        # Show toast
        emoji = "🔴" if severity == "critical" else "🟡"
        self._show_toast(
            f"{emoji} ALERT: {equipment_name} {sensor_type}={value} (>{threshold})",
            "error" if severity == "critical" else "warning"
        )
        
        # Log to database
        try:
            from app.services.database import db
            db.log_alert(
                workflow_id=getattr(self, '_current_workflow_id', ''),
                action_type=action_type,
                recipient=recipient,
                message=alert_content['text'],
                status='sent' if (result and result.success) else 'failed'
            )
        except Exception as e:
            print(f"Error logging alert: {e}")
    
    @rx.event
    async def trigger_manual_alert(self):
        """Manually trigger an alert for testing."""
        nodes = getattr(self, '_cached_nodes', [])
        edges = getattr(self, '_cached_edges', [])
        
        if not nodes:
            self._show_toast("Start simulation first", "warning")
            return
        
        trigger_node = None
        for node in nodes:
            if not node.get('data', {}).get('is_action', False):
                if node.get('data', {}).get('configured', False):
                    trigger_node = node
                    break
        
        if not trigger_node:
            self._show_toast("Configure at least one equipment node", "warning")
            return
        
        action_node = None
        for edge in edges:
            if edge.get('source') == trigger_node['id']:
                target_id = edge.get('target')
                action_node = next((n for n in nodes if n['id'] == target_id), None)
                break
        
        if not action_node:
            self._show_toast("Connect equipment to an action node", "warning")
            return
        
        config = trigger_node.get('data', {}).get('config', {})
        threshold = float(config.get('threshold', 50))
        sensor_type = config.get('sensor_type', 'sensor')
        
        test_value = round(threshold * 1.25, 2)
        
        self._show_toast("🧪 Triggering test alert...", "info")
        
        await self._execute_action(
            trigger_node, action_node, test_value, threshold, sensor_type
        )
    
    def _show_toast(self, message: str, toast_type: str = "info"):
        """Show a toast notification."""
        self.toast_message = message
        self.toast_type = toast_type
        self.show_toast = True
    
    @rx.event
    def hide_toast(self):
        """Hide the toast notification."""
        self.show_toast = False
