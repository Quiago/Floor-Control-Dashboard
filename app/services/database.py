# app/services/database.py
"""
SQLite Database Service for Workflow Persistence.

Handles all database operations for workflows, executions, and alert logs.
Uses SQLite for lightweight demo deployment.
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from pathlib import Path


class DatabaseService:
    """Singleton database service for workflow persistence."""
    
    _instance: Optional['DatabaseService'] = None
    _db_path: str = "data/workflows.db"
    
    def __new__(cls) -> 'DatabaseService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._ensure_db_directory()
        self._init_schema()
    
    def _ensure_db_directory(self):
        """Ensure the data directory exists."""
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_schema(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Workflows table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    nodes_json TEXT NOT NULL,
                    edges_json TEXT NOT NULL,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Workflow executions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    triggered_by TEXT,
                    trigger_data TEXT,
                    status TEXT DEFAULT 'running',
                    result TEXT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
                )
            """)
            
            # Alert logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id INTEGER,
                    workflow_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    recipient TEXT,
                    message TEXT,
                    status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (execution_id) REFERENCES workflow_executions(id),
                    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
                )
            """)
            
            # Sensor data table (for simulation/demo)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    equipment_id TEXT NOT NULL,
                    sensor_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    # --- WORKFLOW CRUD ---
    
    def save_workflow(self, workflow_id: str, name: str, description: str,
                      nodes: List[Dict], edges: List[Dict], status: str = 'draft') -> bool:
        """Save or update a workflow."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO workflows (id, name, description, nodes_json, edges_json, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    description = excluded.description,
                    nodes_json = excluded.nodes_json,
                    edges_json = excluded.edges_json,
                    status = excluded.status,
                    updated_at = excluded.updated_at
            """, (
                workflow_id,
                name,
                description,
                json.dumps(nodes),
                json.dumps(edges),
                status,
                datetime.now().isoformat()
            ))
        return True
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Get a workflow by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_workflow(row)
        return None
    
    def get_all_workflows(self, status: Optional[str] = None) -> List[Dict]:
        """Get all workflows, optionally filtered by status."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM workflows WHERE status = ? ORDER BY updated_at DESC", (status,))
            else:
                cursor.execute("SELECT * FROM workflows ORDER BY updated_at DESC")
            return [self._row_to_workflow(row) for row in cursor.fetchall()]
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM workflows WHERE id = ?", (workflow_id,))
        return True
    
    def update_workflow_status(self, workflow_id: str, status: str) -> bool:
        """Update workflow status (draft, active, paused)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE workflows SET status = ?, updated_at = ? WHERE id = ?",
                (status, datetime.now().isoformat(), workflow_id)
            )
        return True
    
    def _row_to_workflow(self, row: sqlite3.Row) -> Dict:
        """Convert a database row to a workflow dict."""
        return {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'nodes': json.loads(row['nodes_json']),
            'edges': json.loads(row['edges_json']),
            'status': row['status'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
    
    # --- EXECUTION LOGS ---
    
    def log_execution_start(self, workflow_id: str, triggered_by: str, 
                            trigger_data: Dict) -> int:
        """Log the start of a workflow execution."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO workflow_executions (workflow_id, triggered_by, trigger_data, status)
                VALUES (?, ?, ?, 'running')
            """, (workflow_id, triggered_by, json.dumps(trigger_data)))
            return cursor.lastrowid
    
    def log_execution_complete(self, execution_id: int, status: str, result: Dict):
        """Log the completion of a workflow execution."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE workflow_executions 
                SET status = ?, result = ?, completed_at = ?
                WHERE id = ?
            """, (status, json.dumps(result), datetime.now().isoformat(), execution_id))
    
    def get_recent_executions(self, limit: int = 50, workflow_id: Optional[str] = None) -> List[Dict]:
        """Get recent workflow executions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if workflow_id:
                cursor.execute("""
                    SELECT * FROM workflow_executions 
                    WHERE workflow_id = ?
                    ORDER BY started_at DESC LIMIT ?
                """, (workflow_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM workflow_executions 
                    ORDER BY started_at DESC LIMIT ?
                """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # --- ALERT LOGS ---
    
    def log_alert(self, workflow_id: str, action_type: str, recipient: str,
                  message: str, status: str = 'pending', 
                  execution_id: Optional[int] = None,
                  error_message: Optional[str] = None) -> int:
        """Log an alert action."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alert_logs 
                (execution_id, workflow_id, action_type, recipient, message, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (execution_id, workflow_id, action_type, recipient, message, status, error_message))
            return cursor.lastrowid
    
    def update_alert_status(self, alert_id: int, status: str, error_message: Optional[str] = None):
        """Update alert status."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE alert_logs SET status = ?, error_message = ? WHERE id = ?
            """, (status, error_message, alert_id))
    
    def get_recent_alerts(self, limit: int = 100, action_type: Optional[str] = None) -> List[Dict]:
        """Get recent alerts."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if action_type:
                cursor.execute("""
                    SELECT al.*, w.name as workflow_name 
                    FROM alert_logs al
                    LEFT JOIN workflows w ON al.workflow_id = w.id
                    WHERE al.action_type = ?
                    ORDER BY al.created_at DESC LIMIT ?
                """, (action_type, limit))
            else:
                cursor.execute("""
                    SELECT al.*, w.name as workflow_name 
                    FROM alert_logs al
                    LEFT JOIN workflows w ON al.workflow_id = w.id
                    ORDER BY al.created_at DESC LIMIT ?
                """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # --- SENSOR DATA (for demo simulation) ---
    
    def log_sensor_reading(self, equipment_id: str, sensor_type: str, 
                          value: float, unit: str):
        """Log a sensor reading."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sensor_readings (equipment_id, sensor_type, value, unit)
                VALUES (?, ?, ?, ?)
            """, (equipment_id, sensor_type, value, unit))
    
    def get_latest_sensor_reading(self, equipment_id: str, sensor_type: str) -> Optional[Dict]:
        """Get the latest sensor reading for an equipment."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sensor_readings 
                WHERE equipment_id = ? AND sensor_type = ?
                ORDER BY timestamp DESC LIMIT 1
            """, (equipment_id, sensor_type))
            row = cursor.fetchone()
            return dict(row) if row else None


# Global instance
db = DatabaseService()

