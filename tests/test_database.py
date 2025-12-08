# tests/test_database.py
"""Unit tests for DatabaseService."""
import pytest
from datetime import datetime


class TestDatabaseService:
    """Tests for the DatabaseService class."""
    
    def test_save_and_get_workflow(self, temp_db, sample_workflow_data):
        """Test saving and retrieving a workflow."""
        # Save workflow
        temp_db.save_workflow(
            workflow_id=sample_workflow_data["id"],
            name=sample_workflow_data["name"],
            description=sample_workflow_data["description"],
            nodes=sample_workflow_data["nodes"],
            edges=sample_workflow_data["edges"],
            status=sample_workflow_data["status"]
        )
        
        # Retrieve workflow
        workflow = temp_db.get_workflow(sample_workflow_data["id"])
        
        assert workflow is not None
        assert workflow["id"] == sample_workflow_data["id"]
        assert workflow["name"] == sample_workflow_data["name"]
        assert workflow["description"] == sample_workflow_data["description"]
        assert workflow["status"] == sample_workflow_data["status"]
        assert len(workflow["nodes"]) == len(sample_workflow_data["nodes"])
        assert len(workflow["edges"]) == len(sample_workflow_data["edges"])
    
    def test_get_nonexistent_workflow(self, temp_db):
        """Test retrieving a workflow that doesn't exist."""
        workflow = temp_db.get_workflow("nonexistent-id")
        assert workflow is None
    
    def test_get_all_workflows(self, temp_db, sample_workflow_data):
        """Test retrieving all workflows."""
        # Save multiple workflows
        temp_db.save_workflow(
            workflow_id="workflow-1",
            name="Workflow 1",
            description="First workflow",
            nodes=[],
            edges=[],
            status="active"
        )
        temp_db.save_workflow(
            workflow_id="workflow-2",
            name="Workflow 2",
            description="Second workflow",
            nodes=[],
            edges=[],
            status="draft"
        )
        
        # Get all workflows
        all_workflows = temp_db.get_all_workflows()
        assert len(all_workflows) == 2
        
        # Get only active workflows
        active_workflows = temp_db.get_all_workflows(status="active")
        assert len(active_workflows) == 1
        assert active_workflows[0]["id"] == "workflow-1"
    
    def test_delete_workflow(self, temp_db, sample_workflow_data):
        """Test deleting a workflow."""
        # Save workflow
        temp_db.save_workflow(
            workflow_id=sample_workflow_data["id"],
            name=sample_workflow_data["name"],
            description=sample_workflow_data["description"],
            nodes=sample_workflow_data["nodes"],
            edges=sample_workflow_data["edges"],
            status=sample_workflow_data["status"]
        )
        
        # Verify it exists
        assert temp_db.get_workflow(sample_workflow_data["id"]) is not None
        
        # Delete it
        temp_db.delete_workflow(sample_workflow_data["id"])
        
        # Verify it's gone
        assert temp_db.get_workflow(sample_workflow_data["id"]) is None
    
    def test_update_workflow_status(self, temp_db, sample_workflow_data):
        """Test updating workflow status."""
        # Save workflow as draft
        temp_db.save_workflow(
            workflow_id=sample_workflow_data["id"],
            name=sample_workflow_data["name"],
            description=sample_workflow_data["description"],
            nodes=sample_workflow_data["nodes"],
            edges=sample_workflow_data["edges"],
            status="draft"
        )
        
        # Update status to active
        temp_db.update_workflow_status(sample_workflow_data["id"], "active")
        
        # Verify status changed
        workflow = temp_db.get_workflow(sample_workflow_data["id"])
        assert workflow["status"] == "active"
    
    def test_log_execution_start_and_complete(self, temp_db, sample_workflow_data):
        """Test logging execution start and completion."""
        # Save workflow first
        temp_db.save_workflow(
            workflow_id=sample_workflow_data["id"],
            name=sample_workflow_data["name"],
            description=sample_workflow_data["description"],
            nodes=sample_workflow_data["nodes"],
            edges=sample_workflow_data["edges"],
            status="active"
        )
        
        # Start execution
        trigger_data = {"sensor": "temp", "value": 40.0}
        execution_id = temp_db.log_execution_start(
            workflow_id=sample_workflow_data["id"],
            triggered_by="sensor_trigger",
            trigger_data=trigger_data
        )
        
        assert execution_id is not None
        assert execution_id > 0
        
        # Complete execution
        result = {"actions_executed": 1, "success": True}
        temp_db.log_execution_complete(
            execution_id=execution_id,
            status="completed",
            result=result
        )
        
        # Verify execution is logged
        executions = temp_db.get_recent_executions(limit=10)
        assert len(executions) >= 1
    
    def test_log_and_get_alerts(self, temp_db, sample_workflow_data):
        """Test logging and retrieving alerts."""
        # Log an alert
        alert_id = temp_db.log_alert(
            workflow_id=sample_workflow_data["id"],
            action_type="whatsapp",
            recipient="+1234567890",
            message="Test alert message",
            status="pending"
        )
        
        assert alert_id is not None
        
        # Update alert status
        temp_db.update_alert_status(alert_id, "sent")
        
        # Get recent alerts
        alerts = temp_db.get_recent_alerts(limit=10)
        assert len(alerts) >= 1
        
        # Get alerts by type
        whatsapp_alerts = temp_db.get_recent_alerts(limit=10, action_type="whatsapp")
        assert len(whatsapp_alerts) >= 1
    
    def test_sensor_reading_logging(self, temp_db):
        """Test logging and retrieving sensor readings."""
        # Log a sensor reading
        temp_db.log_sensor_reading(
            equipment_id="Centrifuge_01",
            sensor_type="temp",
            value=35.5,
            unit="°C"
        )
        
        # Get latest reading
        reading = temp_db.get_latest_sensor_reading(
            equipment_id="Centrifuge_01",
            sensor_type="temp"
        )
        
        assert reading is not None
        assert reading["value"] == 35.5
        assert reading["unit"] == "°C"
    
    def test_workflow_update_preserves_data(self, temp_db, sample_workflow_data):
        """Test that updating a workflow preserves and updates data correctly."""
        # Save initial workflow
        temp_db.save_workflow(
            workflow_id=sample_workflow_data["id"],
            name=sample_workflow_data["name"],
            description=sample_workflow_data["description"],
            nodes=sample_workflow_data["nodes"],
            edges=sample_workflow_data["edges"],
            status="draft"
        )
        
        # Update with new name
        temp_db.save_workflow(
            workflow_id=sample_workflow_data["id"],
            name="Updated Name",
            description="Updated description",
            nodes=sample_workflow_data["nodes"],
            edges=sample_workflow_data["edges"],
            status="active"
        )
        
        # Verify update
        workflow = temp_db.get_workflow(sample_workflow_data["id"])
        assert workflow["name"] == "Updated Name"
        assert workflow["description"] == "Updated description"
        assert workflow["status"] == "active"
