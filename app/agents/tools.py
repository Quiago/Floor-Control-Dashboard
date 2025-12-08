# app/agents/tools.py
"""LangChain tools for the Nexus AI Agent to interact with the system."""
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from langchain_core.tools import tool

# Import system services
from app.services import db, sensor_simulator
from app.extractors.glb_parser import load_equipment_from_glb


@tool
def list_equipment() -> str:
    """List all equipment available in the 3D factory model.
    
    Returns a list of equipment with their IDs, names, types, and available sensors.
    """
    try:
        equipment = load_equipment_from_glb("assets/pharmaceutical_manufacturing_machinery.glb")
        
        if not equipment:
            return json.dumps({
                "status": "error",
                "message": "No equipment found in the 3D model"
            })
        
        # Format for readability
        result = []
        for eq in equipment:
            result.append({
                "id": eq.get("id", eq.get("name")),
                "name": eq.get("label", eq.get("name")),
                "type": eq.get("type", "unknown"),
                "sensors": [s["name"] for s in eq.get("sensors", [])]
            })
        
        return json.dumps({
            "status": "success",
            "count": len(result),
            "equipment": result
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })


@tool
def get_equipment_status(equipment_id: str) -> str:
    """Get detailed status of specific equipment including sensors, RUL, and dependencies.
    
    Args:
        equipment_id: The ID of the equipment to query (e.g., "Centrifuge_01")
    
    Returns:
        JSON with equipment status, sensor values, RUL percentage, and dependency information.
    """
    try:
        # Get equipment from GLB
        all_equipment = load_equipment_from_glb("assets/pharmaceutical_manufacturing_machinery.glb")
        equipment = next((eq for eq in all_equipment if eq.get("name") == equipment_id or eq.get("id") == equipment_id), None)
        
        if not equipment:
            return json.dumps({
                "status": "error",
                "message": f"Equipment '{equipment_id}' not found"
            })
        
        # Get sensor readings from simulator if registered
        sensor_values = {}
        for sensor in equipment.get("sensors", []):
            sensor_key = f"{equipment_id}.{sensor['id']}"
            info = sensor_simulator.get_sensor_info(sensor_key)
            if info:
                sensor_values[sensor["name"]] = {
                    "value": round(info["current_value"], 2),
                    "unit": info["unit"],
                    "range": [info["min_normal"], info["max_normal"]],
                    "is_anomaly": info.get("is_anomaly", False)
                }
        
        # Simulate RUL and dependencies (would come from knowledge graph in production)
        import random
        result = {
            "status": "success",
            "equipment": {
                "id": equipment_id,
                "name": equipment.get("label", equipment_id),
                "type": equipment.get("type", "unknown"),
                "operational_status": random.choice(["optimal", "optimal", "warning", "optimal"]),
                "rul_percentage": random.randint(60, 98),
                "sensors": sensor_values if sensor_values else "No sensor data available (equipment not registered in simulation)",
                "dependencies": {
                    "depends_on": [f"Feeder-{random.randint(1,5)}", "Power-Unit-Main"],
                    "affects": [f"Packager-{random.randint(10,20)}", "Quality-Gate-B"]
                },
                "last_maintenance": "2024-11-15",
                "production_line": f"Line-{random.choice(['Alpha', 'Beta', 'Gamma'])}"
            }
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })


@tool
def get_sensor_readings(equipment_id: str, sensor_type: Optional[str] = None) -> str:
    """Get current sensor readings for equipment.
    
    Args:
        equipment_id: The equipment to query
        sensor_type: Optional specific sensor type (e.g., "temp", "vibration"). If not provided, returns all sensors.
    
    Returns:
        JSON with current sensor values.
    """
    try:
        values = sensor_simulator.get_current_values()
        
        # Filter by equipment
        filtered = {}
        for key, value in values.items():
            if key.startswith(f"{equipment_id}."):
                sensor_name = key.split(".")[1]
                if sensor_type is None or sensor_name == sensor_type:
                    info = sensor_simulator.get_sensor_info(key)
                    filtered[sensor_name] = {
                        "value": round(value, 2),
                        "unit": info["unit"] if info else "unknown",
                        "is_anomaly": info.get("is_anomaly", False) if info else False
                    }
        
        if not filtered:
            return json.dumps({
                "status": "warning",
                "message": f"No sensor data for '{equipment_id}'. Equipment may not be registered in simulation.",
                "hint": "Try running the simulation first or use get_equipment_status for static info."
            })
        
        return json.dumps({
            "status": "success",
            "equipment_id": equipment_id,
            "timestamp": datetime.now().isoformat(),
            "readings": filtered
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })


@tool
def get_recent_alerts(limit: int = 10, severity: Optional[str] = None) -> str:
    """Get recent alert history from the system.
    
    Args:
        limit: Maximum number of alerts to return (default 10)
        severity: Optional filter by severity ("info", "warning", "critical")
    
    Returns:
        JSON with recent alerts.
    """
    try:
        alerts = db.get_alerts(limit=limit)
        
        if severity:
            alerts = [a for a in alerts if a.get("severity", "").lower() == severity.lower()]
        
        if not alerts:
            return json.dumps({
                "status": "success",
                "message": "No alerts found matching criteria",
                "alerts": []
            })
        
        return json.dumps({
            "status": "success",
            "count": len(alerts),
            "alerts": alerts
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })


@tool
def get_dependencies(equipment_id: str) -> str:
    """Get the dependency graph for equipment showing upstream and downstream connections.
    
    Args:
        equipment_id: The equipment to analyze
    
    Returns:
        JSON with upstream (depends_on) and downstream (affects) equipment.
    """
    try:
        # In production, this would query a real knowledge graph
        import random
        
        result = {
            "status": "success",
            "equipment_id": equipment_id,
            "dependency_graph": {
                "upstream": {
                    "description": "Equipment this depends on (if these fail, this equipment is affected)",
                    "equipment": [
                        {"id": f"Feeder-{random.randint(1,5)}", "type": "feeder", "criticality": "high"},
                        {"id": "Power-Unit-Main", "type": "power", "criticality": "critical"}
                    ]
                },
                "downstream": {
                    "description": "Equipment affected by this (if this fails, these are impacted)",
                    "equipment": [
                        {"id": f"Packager-{random.randint(10,20)}", "type": "packager", "criticality": "medium"},
                        {"id": "Quality-Gate-B", "type": "qc", "criticality": "high"}
                    ]
                }
            },
            "production_impact": {
                "line": f"Line-{random.choice(['Alpha', 'Beta', 'Gamma'])}",
                "product": random.choice(["Vaccine Batch #99", "Serum Vials 50ml", "Antibiotic Strips"])
            }
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })


@tool
def create_workflow(
    name: str,
    trigger_equipment: str,
    trigger_sensor: str,
    trigger_operator: str,
    trigger_threshold: float,
    action_type: str,
    action_target: str,
    severity: str = "warning"
) -> str:
    """Create a new automation workflow. Returns a preview for user approval.
    
    Args:
        name: Name for the workflow
        trigger_equipment: Equipment ID to monitor (e.g., "Centrifuge_01")
        trigger_sensor: Sensor to monitor (e.g., "temp", "vibration", "rpm")
        trigger_operator: Comparison operator (">", "<", ">=", "<=", "==", "between")
        trigger_threshold: Threshold value for the condition
        action_type: Type of action ("whatsapp", "email", "webhook")
        action_target: Target for the action (phone number, email, or URL)
        severity: Alert severity ("info", "warning", "critical")
    
    Returns:
        JSON with workflow preview ready for user approval.
    """
    try:
        import uuid
        
        workflow_preview = {
            "status": "pending_approval",
            "workflow_id": f"wf_{uuid.uuid4().hex[:8]}",
            "name": name,
            "trigger": {
                "equipment": trigger_equipment,
                "sensor": trigger_sensor,
                "condition": f"{trigger_operator} {trigger_threshold}"
            },
            "action": {
                "type": action_type,
                "target": action_target,
                "severity": severity
            },
            "summary": f"When {trigger_equipment}.{trigger_sensor} {trigger_operator} {trigger_threshold}, send {action_type} alert to {action_target}",
            "instructions": "This workflow is ready for activation. Please confirm to proceed."
        }
        
        return json.dumps(workflow_preview, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })


@tool
def get_execution_logs(workflow_id: Optional[str] = None, limit: int = 10) -> str:
    """Get workflow execution history.
    
    Args:
        workflow_id: Optional workflow ID to filter by
        limit: Maximum number of logs to return
    
    Returns:
        JSON with execution logs.
    """
    try:
        if workflow_id:
            logs = db.get_execution_logs(workflow_id, limit=limit)
        else:
            # Get all recent executions
            workflows = db.get_all_workflows()
            logs = []
            for wf in workflows[:5]:  # Limit to 5 workflows
                wf_logs = db.get_execution_logs(wf["id"], limit=2)
                logs.extend(wf_logs)
        
        if not logs:
            return json.dumps({
                "status": "success",
                "message": "No execution logs found",
                "logs": []
            })
        
        return json.dumps({
            "status": "success",
            "count": len(logs),
            "logs": logs[:limit]
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })


# Export all tools for easy import
ALL_TOOLS = [
    list_equipment,
    get_equipment_status,
    get_sensor_readings,
    get_recent_alerts,
    get_dependencies,
    create_workflow,
    get_execution_logs,
]
