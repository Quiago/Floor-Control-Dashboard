# tests/conftest.py
"""Pytest fixtures for Floor Control Dashboard tests."""
import pytest
import tempfile
import os
import shutil
from pathlib import Path


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_workflows.db")
    yield db_path
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_db(temp_db_path):
    """Create a temporary DatabaseService instance."""
    from app.services.database import DatabaseService
    
    # Create a new instance with custom path
    service = DatabaseService.__new__(DatabaseService)
    service._initialized = False
    service._db_path = temp_db_path
    service.__init__()
    
    yield service


@pytest.fixture
def mock_notification_config():
    """Create a notification config in mock mode."""
    from app.services.notification_service import NotificationConfig
    
    # Ensure mock mode
    original_env = os.environ.get('NOTIFICATION_MOCK_MODE')
    os.environ['NOTIFICATION_MOCK_MODE'] = 'true'
    
    config = NotificationConfig()
    
    yield config
    
    # Restore
    if original_env is not None:
        os.environ['NOTIFICATION_MOCK_MODE'] = original_env
    else:
        os.environ.pop('NOTIFICATION_MOCK_MODE', None)


@pytest.fixture
def mock_notification_service(mock_notification_config):
    """Create a notification service in mock mode."""
    from app.services.notification_service import NotificationService
    
    service = NotificationService(config=mock_notification_config)
    yield service


@pytest.fixture
def sensor_simulator():
    """Create a fresh SensorSimulator instance."""
    from app.services.sensor_simulator import SensorSimulator
    
    simulator = SensorSimulator()
    yield simulator


@pytest.fixture
def sample_workflow_data():
    """Sample workflow data for testing."""
    return {
        "id": "test-workflow-001",
        "name": "Test Temperature Alert",
        "description": "Alert when temperature exceeds threshold",
        "nodes": [
            {
                "id": "node-1",
                "type": "equipment",
                "label": "Centrifuge_01",
                "category": "centrifuge",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Centrifuge_01",
                    "category": "centrifuge",
                    "configured": True,
                    "config": {
                        "equipment_id": "Centrifuge_01",
                        "sensor_type": "temp",
                        "operator": ">",
                        "threshold": 35.0,
                        "severity": "warning"
                    }
                }
            },
            {
                "id": "node-2",
                "type": "action",
                "label": "WhatsApp Alert",
                "category": "whatsapp",
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "WhatsApp Alert",
                    "category": "whatsapp",
                    "is_action": True,
                    "configured": True,
                    "config": {
                        "phone_number": "+1234567890",
                        "severity": "warning"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1-2",
                "source": "node-1",
                "target": "node-2"
            }
        ],
        "status": "active"
    }


@pytest.fixture
def sample_sensor_data():
    """Sample sensor data for testing."""
    return {
        "Centrifuge_01.temp": 40.0,  # Above threshold (35)
        "Centrifuge_01.rpm": 4000.0,
        "Centrifuge_01.vibration": 2.0,
        "Analyzer_01.temp": 22.0,
        "Analyzer_01.ph": 7.0
    }
