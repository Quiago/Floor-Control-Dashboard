# tests/test_workflow_engine.py
"""Unit tests for WorkflowEngine."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestConditionEvaluation:
    """Tests for condition evaluation logic."""
    
    def test_evaluate_condition_greater_than_true(self):
        """Test > operator returns True when value exceeds threshold."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        result = engine.evaluate_condition(
            value=45.0,
            operator=">",
            threshold=35.0
        )
        
        assert result is True
    
    def test_evaluate_condition_greater_than_false(self):
        """Test > operator returns False when value is below threshold."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        result = engine.evaluate_condition(
            value=30.0,
            operator=">",
            threshold=35.0
        )
        
        assert result is False
    
    def test_evaluate_condition_less_than_true(self):
        """Test < operator returns True when value is below threshold."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        result = engine.evaluate_condition(
            value=15.0,
            operator="<",
            threshold=20.0
        )
        
        assert result is True
    
    def test_evaluate_condition_less_than_false(self):
        """Test < operator returns False when value exceeds threshold."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        result = engine.evaluate_condition(
            value=25.0,
            operator="<",
            threshold=20.0
        )
        
        assert result is False
    
    def test_evaluate_condition_equals_true(self):
        """Test == operator returns True when values match."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        result = engine.evaluate_condition(
            value=7.0,
            operator="==",
            threshold=7.0
        )
        
        assert result is True
    
    def test_evaluate_condition_equals_false(self):
        """Test == operator returns False when values don't match."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        result = engine.evaluate_condition(
            value=7.5,
            operator="==",
            threshold=7.0
        )
        
        assert result is False
    
    def test_evaluate_condition_not_equals_true(self):
        """Test != operator returns True when values differ."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        result = engine.evaluate_condition(
            value=7.5,
            operator="!=",
            threshold=7.0
        )
        
        assert result is True
    
    def test_evaluate_condition_greater_or_equal_true(self):
        """Test >= operator returns True when value meets or exceeds threshold."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        
        # Equal case
        result1 = engine.evaluate_condition(
            value=35.0,
            operator=">=",
            threshold=35.0
        )
        assert result1 is True
        
        # Greater case
        result2 = engine.evaluate_condition(
            value=40.0,
            operator=">=",
            threshold=35.0
        )
        assert result2 is True
    
    def test_evaluate_condition_less_or_equal_true(self):
        """Test <= operator returns True when value meets or is below threshold."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        
        # Equal case
        result1 = engine.evaluate_condition(
            value=20.0,
            operator="<=",
            threshold=20.0
        )
        assert result1 is True
        
        # Less case
        result2 = engine.evaluate_condition(
            value=15.0,
            operator="<=",
            threshold=20.0
        )
        assert result2 is True
    
    def test_evaluate_condition_between_true(self):
        """Test between operator returns True when value is in range."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        result = engine.evaluate_condition(
            value=25.0,
            operator="between",
            threshold=20.0,
            threshold_max=30.0
        )
        
        assert result is True
    
    def test_evaluate_condition_between_false(self):
        """Test between operator returns False when value is outside range."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        result = engine.evaluate_condition(
            value=35.0,
            operator="between",
            threshold=20.0,
            threshold_max=30.0
        )
        
        assert result is False
    
    def test_evaluate_condition_not_between_true(self):
        """Test not_between operator returns True when value is outside range."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        result = engine.evaluate_condition(
            value=35.0,
            operator="not_between",
            threshold=20.0,
            threshold_max=30.0
        )
        
        assert result is True
    
    def test_evaluate_condition_not_between_false(self):
        """Test not_between operator returns False when value is in range."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        result = engine.evaluate_condition(
            value=25.0,
            operator="not_between",
            threshold=20.0,
            threshold_max=30.0
        )
        
        assert result is False


class TestWorkflowExecution:
    """Tests for workflow execution."""
    
    @pytest.mark.asyncio
    async def test_execute_workflow_with_matching_condition(self, temp_db, sample_workflow_data, sample_sensor_data):
        """Test executing a workflow when conditions match."""
        from app.services.workflow_engine import WorkflowEngine
        from app.services.notification_service import NotificationService, NotificationConfig
        import os
        
        # Ensure mock mode
        os.environ['NOTIFICATION_MOCK_MODE'] = 'true'
        mock_config = NotificationConfig()
        mock_notif = NotificationService(config=mock_config)
        
        # Save workflow to temp db
        temp_db.save_workflow(
            workflow_id=sample_workflow_data["id"],
            name=sample_workflow_data["name"],
            description=sample_workflow_data["description"],
            nodes=sample_workflow_data["nodes"],
            edges=sample_workflow_data["edges"],
            status="active"
        )
        
        # Create engine with our services
        engine = WorkflowEngine(db_service=temp_db, notif_service=mock_notif)
        
        # Execute workflow
        context = await engine.execute_workflow(
            workflow_id=sample_workflow_data["id"],
            sensor_data=sample_sensor_data
        )
        
        assert context is not None
        assert context.workflow_id == sample_workflow_data["id"]
        
        await mock_notif.close()
    
    @pytest.mark.asyncio
    async def test_execute_workflow_no_matching_condition(self, temp_db, sample_workflow_data):
        """Test executing a workflow when no conditions match."""
        from app.services.workflow_engine import WorkflowEngine
        from app.services.notification_service import NotificationService, NotificationConfig
        import os
        
        os.environ['NOTIFICATION_MOCK_MODE'] = 'true'
        mock_config = NotificationConfig()
        mock_notif = NotificationService(config=mock_config)
        
        temp_db.save_workflow(
            workflow_id=sample_workflow_data["id"],
            name=sample_workflow_data["name"],
            description=sample_workflow_data["description"],
            nodes=sample_workflow_data["nodes"],
            edges=sample_workflow_data["edges"],
            status="active"
        )
        
        engine = WorkflowEngine(db_service=temp_db, notif_service=mock_notif)
        
        # Sensor data that does NOT trigger (temp below threshold)
        non_triggering_data = {
            "Centrifuge_01.temp": 30.0,  # Below threshold of 35
        }
        
        context = await engine.execute_workflow(
            workflow_id=sample_workflow_data["id"],
            sensor_data=non_triggering_data
        )
        
        # Workflow should execute but no actions triggered
        assert context is not None
        
        await mock_notif.close()
    
    @pytest.mark.asyncio
    async def test_test_workflow_preview(self, temp_db, sample_workflow_data):
        """Test workflow preview mode without persistence."""
        from app.services.workflow_engine import WorkflowEngine
        from app.services.notification_service import NotificationService, NotificationConfig
        import os
        
        os.environ['NOTIFICATION_MOCK_MODE'] = 'true'
        mock_config = NotificationConfig()
        mock_notif = NotificationService(config=mock_config)
        
        temp_db.save_workflow(
            workflow_id=sample_workflow_data["id"],
            name=sample_workflow_data["name"],
            description=sample_workflow_data["description"],
            nodes=sample_workflow_data["nodes"],
            edges=sample_workflow_data["edges"],
            status="active"
        )
        
        engine = WorkflowEngine(db_service=temp_db, notif_service=mock_notif)
        
        # Test workflow (should generate mock data)
        result = await engine.test_workflow(
            workflow_id=sample_workflow_data["id"]
        )
        
        assert result is not None
        # test_workflow returns a dict with 'workflow_name', 'mock_data', 'trigger_results'
        assert isinstance(result, dict)
        assert "workflow_name" in result
        
        await mock_notif.close()
    
    @pytest.mark.asyncio
    async def test_test_workflow_with_custom_data(self, temp_db, sample_workflow_data, sample_sensor_data):
        """Test workflow preview with custom sensor data."""
        from app.services.workflow_engine import WorkflowEngine
        from app.services.notification_service import NotificationService, NotificationConfig
        import os
        
        os.environ['NOTIFICATION_MOCK_MODE'] = 'true'
        mock_config = NotificationConfig()
        mock_notif = NotificationService(config=mock_config)
        
        temp_db.save_workflow(
            workflow_id=sample_workflow_data["id"],
            name=sample_workflow_data["name"],
            description=sample_workflow_data["description"],
            nodes=sample_workflow_data["nodes"],
            edges=sample_workflow_data["edges"],
            status="active"
        )
        
        engine = WorkflowEngine(db_service=temp_db, notif_service=mock_notif)
        
        result = await engine.test_workflow(
            workflow_id=sample_workflow_data["id"],
            mock_sensor_data=sample_sensor_data
        )
        
        assert result is not None
        
        await mock_notif.close()


class TestAdjacencyMap:
    """Tests for graph traversal helpers."""
    
    def test_build_adjacency_map_simple(self):
        """Test building adjacency map from edges."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        edges = [
            {"source": "node-1", "target": "node-2"},
            {"source": "node-1", "target": "node-3"},
            {"source": "node-2", "target": "node-4"}
        ]
        
        adjacency = engine._build_adjacency_map(edges)
        
        assert "node-1" in adjacency
        assert "node-2" in adjacency["node-1"]
        assert "node-3" in adjacency["node-1"]
        assert "node-4" in adjacency["node-2"]
    
    def test_build_adjacency_map_empty(self):
        """Test building adjacency map with no edges."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        adjacency = engine._build_adjacency_map([])
        
        assert adjacency == {}
    
    def test_get_connected_nodes(self):
        """Test getting nodes connected to a source."""
        from app.services.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        nodes = [
            {"id": "node-1", "data": {"label": "Source"}},
            {"id": "node-2", "data": {"label": "Target A"}},
            {"id": "node-3", "data": {"label": "Target B"}}
        ]
        adjacency = {"node-1": ["node-2", "node-3"]}
        
        connected = engine._get_connected_nodes("node-1", adjacency, nodes)
        
        assert len(connected) == 2
        assert any(n["id"] == "node-2" for n in connected)
        assert any(n["id"] == "node-3" for n in connected)
