# app/services/workflow_service.py
"""
Shared Workflow Service - Used by both WorkflowState and AgentState.

Provides a stateless service for workflow operations that can be called
from any state without causing re-renders in other states.
"""
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime


class WorkflowService:
    """Shared service for workflow operations."""
    
    # Node styling configuration
    EQUIPMENT_COLORS = {
        'analyzer': {'bg': '#581c87', 'border': '#a855f7'},
        'robot': {'bg': '#1e3a8a', 'border': '#3b82f6'},
        'centrifuge': {'bg': '#164e63', 'border': '#22d3ee'},
        'storage': {'bg': '#14532d', 'border': '#22c55e'},
        'conveyor': {'bg': '#713f12', 'border': '#eab308'},
    }
    
    ACTION_COLORS = {
        'whatsapp': {'bg': '#166534', 'border': '#22c55e'},
        'email': {'bg': '#1e40af', 'border': '#3b82f6'},
        'alert': {'bg': '#991b1b', 'border': '#ef4444'},
        'webhook': {'bg': '#374151', 'border': '#6b7280'},
    }
    
    CATEGORY_INFO = {
        'analyzer': {'name': 'Analyzer', 'icon': 'scan'},
        'robot': {'name': 'Robot', 'icon': 'box'},
        'centrifuge': {'name': 'Centrifuge', 'icon': 'circle-dot'},
        'storage': {'name': 'Storage', 'icon': 'package'},
        'conveyor': {'name': 'Conveyor', 'icon': 'arrow-right'},
        'whatsapp': {'name': 'WhatsApp', 'icon': 'message-circle'},
        'email': {'name': 'Email', 'icon': 'mail'},
        'alert': {'name': 'System Alert', 'icon': 'bell'},
        'webhook': {'name': 'Webhook', 'icon': 'globe'},
    }
    
    def create_workflow_from_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow nodes and edges from a specification.
        
        Args:
            spec: {
                "name": str,
                "trigger_equipment": str,
                "trigger_sensor": str,
                "trigger_operator": str,
                "trigger_threshold": float,
                "action_type": str,
                "action_target": str,
                "severity": str
            }
        
        Returns:
            {
                "workflow_id": str,
                "name": str,
                "nodes": list,
                "edges": list,
                "status": str
            }
        """
        workflow_id = f"wf_{uuid.uuid4().hex[:12]}"
        
        # Determine equipment category from equipment name
        equipment_category = self._infer_equipment_category(spec.get('trigger_equipment', ''))
        action_type = spec.get('action_type', 'alert')
        
        # Create equipment node
        equipment_node = self._create_node(
            node_id="node_1",
            category=equipment_category,
            label=spec.get('trigger_equipment', 'Equipment'),
            is_action=False,
            position={'x': 200, 'y': 200},
            config={
                'sensor_type': spec.get('trigger_sensor', 'temp'),
                'operator': spec.get('trigger_operator', '>'),
                'threshold': spec.get('trigger_threshold', 50),
                'severity': spec.get('severity', 'warning'),
                'specific_equipment_id': spec.get('trigger_equipment', ''),
                'equipment_id': 'node_1'
            }
        )
        
        # Create action node
        action_config = {
            'severity': spec.get('severity', 'warning')
        }
        
        # Set action-specific config
        action_target = spec.get('action_target', '')
        if action_type == 'whatsapp':
            action_config['phone_number'] = action_target
        elif action_type == 'email':
            action_config['email'] = action_target
        elif action_type == 'webhook':
            action_config['webhook_url'] = action_target
        
        action_node = self._create_node(
            node_id="node_2",
            category=action_type,
            label=f"{self.CATEGORY_INFO.get(action_type, {}).get('name', action_type)}",
            is_action=True,
            position={'x': 500, 'y': 200},
            config=action_config
        )
        
        # Create edge connecting equipment to action
        edge = {
            'id': 'edge_node_1_node_2',
            'source': 'node_1',
            'target': 'node_2',
            'type': 'smoothstep',
            'animated': True,
            'style': {'stroke': '#3b82f6', 'strokeWidth': 2}
        }
        
        return {
            'workflow_id': workflow_id,
            'name': spec.get('name', 'New Workflow'),
            'nodes': [equipment_node, action_node],
            'edges': [edge],
            'status': 'active'
        }
    
    def _infer_equipment_category(self, equipment_name: str) -> str:
        """Infer equipment category from name."""
        name_lower = equipment_name.lower()
        
        if 'centrifuge' in name_lower:
            return 'centrifuge'
        elif 'robot' in name_lower or 'arm' in name_lower:
            return 'robot'
        elif 'analyzer' in name_lower or 'scan' in name_lower:
            return 'analyzer'
        elif 'storage' in name_lower or 'tank' in name_lower:
            return 'storage'
        elif 'conveyor' in name_lower or 'belt' in name_lower:
            return 'conveyor'
        else:
            return 'analyzer'  # Default
    
    def _create_node(self, node_id: str, category: str, label: str,
                     is_action: bool, position: Dict, config: Dict) -> Dict:
        """Create a styled node."""
        if is_action:
            colors = self.ACTION_COLORS.get(category, self.ACTION_COLORS['alert'])
        else:
            colors = self.EQUIPMENT_COLORS.get(category, self.EQUIPMENT_COLORS['analyzer'])
        
        return {
            'id': node_id,
            'type': 'default',
            'position': position,
            'data': {
                'label': label,
                'category': category,
                'is_action': is_action,
                'configured': True,
                'config': config
            },
            'style': {
                'background': colors['bg'],
                'color': 'white',
                'border': f"2px solid {colors['border']}",
                'borderRadius': '8px',
                'padding': '10px 15px',
                'fontSize': '12px',
                'fontWeight': '500',
                'minWidth': '120px',
                'textAlign': 'center',
                'cursor': 'pointer',
                'boxShadow': '0 0 10px rgba(34, 197, 94, 0.5)'  # Configured indicator
            },
            'sourcePosition': 'right',
            'targetPosition': 'left',
        }
    
    def save_workflow(self, workflow_id: str, name: str, nodes: List[Dict],
                      edges: List[Dict], status: str = "active") -> bool:
        """Save workflow to database.

        Args:
            workflow_id: Unique workflow ID
            name: Workflow name
            nodes: List of nodes
            edges: List of edges
            status: Workflow status (draft, active, paused)

        Returns:
            True if successful
        """
        print(f"[WorkflowService.save_workflow] >>> ENTRY: id={workflow_id}, name={name}")
        try:
            print("[WorkflowService.save_workflow] >>> Importing db...")
            from app.services.database import db

            print("[WorkflowService.save_workflow] >>> Calling db.save_workflow()...")
            db.save_workflow(
                workflow_id=workflow_id,
                name=name,
                description="",
                nodes=nodes,
                edges=edges,
                status=status
            )
            print("[WorkflowService.save_workflow] >>> db.save_workflow() returned")
            print("[WorkflowService.save_workflow] >>> EXIT: success=True")
            return True
        except Exception as e:
            print(f"[WorkflowService.save_workflow] !!! ERROR: {e}")
            print(f"[WorkflowService.save_workflow] >>> EXIT: success=False")
            return False
    
    def load_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Load workflow from database."""
        try:
            from app.services.database import db
            return db.get_workflow(workflow_id)
        except Exception as e:
            print(f"Error loading workflow: {e}")
            return None
    
    def activate_workflow(self, workflow_id: str) -> bool:
        """Activate a workflow."""
        try:
            from app.services.database import db
            workflow = db.get_workflow(workflow_id)
            if workflow:
                db.save_workflow(
                    workflow_id=workflow_id,
                    name=workflow['name'],
                    description=workflow.get('description', ''),
                    nodes=workflow['nodes'],
                    edges=workflow['edges'],
                    status='active'
                )
                return True
            return False
        except Exception as e:
            print(f"Error activating workflow: {e}")
            return False
    
    def get_active_workflows(self) -> List[Dict]:
        """Get all active workflows."""
        try:
            from app.services.database import db
            return db.get_all_workflows(status="active")
        except Exception as e:
            print(f"Error getting active workflows: {e}")
            return []


# Singleton instance
workflow_service = WorkflowService()
