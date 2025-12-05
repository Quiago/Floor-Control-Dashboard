# app/services/workflow_engine.py
"""
Workflow Execution Engine.

Evaluates workflow conditions and executes actions based on sensor data.
Supports threshold comparisons, pattern detection, and action dispatching.
"""
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from .database import db, DatabaseService
from .notification_service import notification_service, NotificationService, AlertTemplates


class ConditionOperator(Enum):
    """Supported condition operators."""
    GREATER_THAN = ">"
    LESS_THAN = "<"
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_OR_EQUAL = ">="
    LESS_OR_EQUAL = "<="
    BETWEEN = "between"
    NOT_BETWEEN = "not_between"


class ActionType(Enum):
    """Supported action types."""
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    WEBHOOK = "webhook"
    LOG = "log"
    SYSTEM_ALERT = "system_alert"


@dataclass
class WorkflowExecutionContext:
    """Context for workflow execution."""
    workflow_id: str
    workflow_name: str
    execution_id: Optional[int] = None
    trigger_data: Dict = None
    results: List[Dict] = None
    
    def __post_init__(self):
        if self.trigger_data is None:
            self.trigger_data = {}
        if self.results is None:
            self.results = []


class WorkflowEngine:
    """
    Engine for evaluating and executing workflows.
    
    Workflow structure:
    - Nodes: Equipment sensors (triggers) and Actions
    - Edges: Connections defining flow
    - Each node has configuration (thresholds, recipients, etc.)
    """
    
    def __init__(self, db_service: Optional[DatabaseService] = None,
                 notif_service: Optional[NotificationService] = None):
        self.db = db_service or db
        self.notifications = notif_service or notification_service
    
    # --- CONDITION EVALUATION ---
    
    def evaluate_condition(self, value: float, operator: str, 
                          threshold: float, threshold_max: Optional[float] = None) -> bool:
        """
        Evaluate a threshold condition.
        
        Args:
            value: Current sensor value
            operator: Comparison operator
            threshold: Threshold value (or min for between)
            threshold_max: Max value for between operators
        
        Returns:
            True if condition is met (alert should trigger)
        """
        try:
            op = ConditionOperator(operator)
            
            if op == ConditionOperator.GREATER_THAN:
                return value > threshold
            elif op == ConditionOperator.LESS_THAN:
                return value < threshold
            elif op == ConditionOperator.EQUALS:
                return abs(value - threshold) < 0.0001  # Float comparison
            elif op == ConditionOperator.NOT_EQUALS:
                return abs(value - threshold) >= 0.0001
            elif op == ConditionOperator.GREATER_OR_EQUAL:
                return value >= threshold
            elif op == ConditionOperator.LESS_OR_EQUAL:
                return value <= threshold
            elif op == ConditionOperator.BETWEEN:
                return threshold <= value <= (threshold_max or threshold)
            elif op == ConditionOperator.NOT_BETWEEN:
                return not (threshold <= value <= (threshold_max or threshold))
            else:
                return False
                
        except ValueError:
            print(f"Unknown operator: {operator}")
            return False
    
    # --- WORKFLOW EXECUTION ---
    
    async def execute_workflow(self, workflow_id: str, 
                              sensor_data: Dict[str, float]) -> WorkflowExecutionContext:
        """
        Execute a workflow based on sensor data.
        
        Args:
            workflow_id: ID of the workflow to execute
            sensor_data: Dict of sensor_id -> current_value
        
        Returns:
            ExecutionContext with results
        """
        # Load workflow
        workflow = self.db.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        if workflow['status'] != 'active':
            raise ValueError(f"Workflow is not active: {workflow_id}")
        
        # Create execution context
        ctx = WorkflowExecutionContext(
            workflow_id=workflow_id,
            workflow_name=workflow['name'],
            trigger_data=sensor_data
        )
        
        # Log execution start
        ctx.execution_id = self.db.log_execution_start(
            workflow_id, 
            triggered_by="sensor_check",
            trigger_data=sensor_data
        )
        
        try:
            nodes = workflow['nodes']
            edges = workflow['edges']
            
            # Build adjacency map
            adjacency = self._build_adjacency_map(edges)
            
            # Find trigger nodes (equipment with sensors)
            trigger_nodes = [n for n in nodes if n['data'].get('category') in 
                          ['analyzer', 'robot', 'centrifuge', 'storage', 'conveyor']]
            
            # Evaluate each trigger
            triggered_actions = []
            
            for trigger_node in trigger_nodes:
                node_config = trigger_node['data'].get('config', {})
                if not node_config:
                    continue
                
                # Check if this node's sensor triggered
                equipment_id = node_config.get('equipment_id', trigger_node['id'])
                sensor_type = node_config.get('sensor_type')
                
                if not sensor_type:
                    continue
                
                sensor_key = f"{equipment_id}.{sensor_type}"
                current_value = sensor_data.get(sensor_key)
                
                if current_value is None:
                    continue
                
                # Evaluate condition
                operator = node_config.get('operator', '>')
                threshold = node_config.get('threshold', 0)
                threshold_max = node_config.get('threshold_max')
                
                if self.evaluate_condition(current_value, operator, threshold, threshold_max):
                    # Condition met - find connected action nodes
                    connected_actions = self._get_connected_nodes(
                        trigger_node['id'], adjacency, nodes
                    )
                    
                    for action_node in connected_actions:
                        triggered_actions.append({
                            'trigger_node': trigger_node,
                            'action_node': action_node,
                            'sensor_value': current_value,
                            'threshold': threshold,
                            'equipment_id': equipment_id,
                            'sensor_type': sensor_type
                        })
            
            # Execute triggered actions
            for action_info in triggered_actions:
                result = await self._execute_action(action_info, ctx)
                ctx.results.append(result)
            
            # Log completion
            self.db.log_execution_complete(
                ctx.execution_id,
                status='success' if all(r.get('success') for r in ctx.results) else 'partial',
                result={'actions_executed': len(ctx.results), 'results': ctx.results}
            )
            
        except Exception as e:
            self.db.log_execution_complete(
                ctx.execution_id,
                status='error',
                result={'error': str(e)}
            )
            raise
        
        return ctx
    
    async def _execute_action(self, action_info: Dict, 
                             ctx: WorkflowExecutionContext) -> Dict:
        """Execute a single action node."""
        action_node = action_info['action_node']
        trigger_node = action_info['trigger_node']
        action_config = action_node['data'].get('config', {})
        action_type = action_node['data'].get('category', '')
        
        # Get equipment info for message
        equipment_name = trigger_node['data'].get('label', trigger_node['id'])
        sensor_type = action_info['sensor_type']
        sensor_value = action_info['sensor_value']
        threshold = action_info['threshold']
        
        # Determine severity
        severity = action_config.get('severity', 'warning')
        
        # Generate message from template
        alert_content = AlertTemplates.threshold_alert(
            equipment_name=equipment_name,
            sensor=sensor_type,
            value=sensor_value,
            threshold=threshold,
            unit=action_config.get('unit', ''),
            severity=severity
        )
        
        result = {
            'action_type': action_type,
            'action_node_id': action_node['id'],
            'trigger_node_id': trigger_node['id'],
            'success': False
        }
        
        try:
            if action_type == 'whatsapp':
                recipient = action_config.get('phone_number', '')
                if recipient:
                    notif_result = await self.notifications.send_whatsapp(
                        recipient, alert_content['text']
                    )
                    result['success'] = notif_result.success
                    result['message_id'] = notif_result.message_id
                    result['error'] = notif_result.error
                    
                    # Log alert
                    self.db.log_alert(
                        workflow_id=ctx.workflow_id,
                        action_type='whatsapp',
                        recipient=recipient,
                        message=alert_content['text'],
                        status='sent' if notif_result.success else 'failed',
                        execution_id=ctx.execution_id,
                        error_message=notif_result.error
                    )
            
            elif action_type == 'email':
                recipient = action_config.get('email', '')
                if recipient:
                    notif_result = await self.notifications.send_email(
                        recipient,
                        alert_content['subject'],
                        alert_content['text'],
                        html_body=alert_content.get('html')
                    )
                    result['success'] = notif_result.success
                    result['message_id'] = notif_result.message_id
                    result['error'] = notif_result.error
                    
                    # Log alert
                    self.db.log_alert(
                        workflow_id=ctx.workflow_id,
                        action_type='email',
                        recipient=recipient,
                        message=alert_content['text'],
                        status='sent' if notif_result.success else 'failed',
                        execution_id=ctx.execution_id,
                        error_message=notif_result.error
                    )
            
            elif action_type == 'alert':
                # System alert - log to database
                self.db.log_alert(
                    workflow_id=ctx.workflow_id,
                    action_type='system_alert',
                    recipient='system',
                    message=alert_content['text'],
                    status='logged',
                    execution_id=ctx.execution_id
                )
                result['success'] = True
            
            elif action_type == 'webhook':
                webhook_url = action_config.get('url', '')
                if webhook_url:
                    payload = {
                        'workflow_id': ctx.workflow_id,
                        'equipment': equipment_name,
                        'sensor': sensor_type,
                        'value': sensor_value,
                        'threshold': threshold,
                        'severity': severity,
                        'timestamp': datetime.now().isoformat()
                    }
                    notif_result = await self.notifications.send_webhook(webhook_url, payload)
                    result['success'] = notif_result.success
                    result['error'] = notif_result.error
                    
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _build_adjacency_map(self, edges: List[Dict]) -> Dict[str, List[str]]:
        """Build adjacency map from edges."""
        adjacency = {}
        for edge in edges:
            source = edge.get('source', '')
            target = edge.get('target', '')
            if source not in adjacency:
                adjacency[source] = []
            adjacency[source].append(target)
        return adjacency
    
    def _get_connected_nodes(self, node_id: str, adjacency: Dict[str, List[str]], 
                            nodes: List[Dict]) -> List[Dict]:
        """Get nodes connected to given node."""
        connected_ids = adjacency.get(node_id, [])
        nodes_map = {n['id']: n for n in nodes}
        return [nodes_map[nid] for nid in connected_ids if nid in nodes_map]
    
    # --- SIMULATION / TESTING ---
    
    async def test_workflow(self, workflow_id: str, 
                           mock_sensor_data: Optional[Dict[str, float]] = None) -> Dict:
        """
        Test a workflow with mock data without saving execution logs.
        
        Returns a preview of what would happen.
        """
        workflow = self.db.get_workflow(workflow_id)
        if not workflow:
            return {'error': f'Workflow not found: {workflow_id}'}
        
        nodes = workflow['nodes']
        edges = workflow['edges']
        
        # Generate mock data if not provided
        if mock_sensor_data is None:
            mock_sensor_data = self._generate_mock_sensor_data(nodes)
        
        # Preview what would trigger
        adjacency = self._build_adjacency_map(edges)
        results = []
        
        trigger_nodes = [n for n in nodes if n['data'].get('category') in 
                        ['analyzer', 'robot', 'centrifuge', 'storage', 'conveyor']]
        
        for trigger_node in trigger_nodes:
            node_config = trigger_node['data'].get('config', {})
            if not node_config:
                continue
            
            equipment_id = node_config.get('equipment_id', trigger_node['id'])
            sensor_type = node_config.get('sensor_type')
            
            if not sensor_type:
                continue
            
            sensor_key = f"{equipment_id}.{sensor_type}"
            current_value = mock_sensor_data.get(sensor_key, 0)
            
            operator = node_config.get('operator', '>')
            threshold = node_config.get('threshold', 0)
            
            would_trigger = self.evaluate_condition(current_value, operator, threshold)
            
            connected = self._get_connected_nodes(trigger_node['id'], adjacency, nodes)
            
            results.append({
                'trigger_node': trigger_node['data'].get('label', trigger_node['id']),
                'sensor': sensor_type,
                'current_value': current_value,
                'threshold': threshold,
                'operator': operator,
                'would_trigger': would_trigger,
                'connected_actions': [a['data'].get('label', a['id']) for a in connected]
            })
        
        return {
            'workflow_name': workflow['name'],
            'mock_data': mock_sensor_data,
            'trigger_results': results
        }
    
    def _generate_mock_sensor_data(self, nodes: List[Dict]) -> Dict[str, float]:
        """Generate mock sensor data that would trigger some nodes."""
        import random
        mock_data = {}
        
        for node in nodes:
            config = node['data'].get('config', {})
            if not config:
                continue
            
            equipment_id = config.get('equipment_id', node['id'])
            sensor_type = config.get('sensor_type')
            threshold = config.get('threshold', 50)
            operator = config.get('operator', '>')
            
            if not sensor_type:
                continue
            
            # Generate value that sometimes triggers, sometimes doesn't
            if random.random() > 0.5:
                # Generate triggering value
                if operator in ('>', '>='):
                    value = threshold + random.uniform(5, 20)
                elif operator in ('<', '<='):
                    value = threshold - random.uniform(5, 20)
                else:
                    value = threshold
            else:
                # Generate non-triggering value
                if operator in ('>', '>='):
                    value = threshold - random.uniform(5, 20)
                else:
                    value = threshold + random.uniform(5, 20)
            
            mock_data[f"{equipment_id}.{sensor_type}"] = round(value, 2)
        
        return mock_data


# Global instance
workflow_engine = WorkflowEngine()

