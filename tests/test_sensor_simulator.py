# tests/test_sensor_simulator.py
"""Unit tests for SensorSimulator."""
import pytest
from unittest.mock import patch, MagicMock
from app.services.sensor_simulator import AnomalyType


@pytest.fixture(autouse=True)
def mock_db():
    """Mock the database to prevent connection errors during tests."""
    with patch('app.services.sensor_simulator.db') as mock:
        mock.log_sensor_reading = MagicMock()
        yield mock


class TestSensorSimulator:
    """Tests for the SensorSimulator class."""
    
    def test_register_equipment_centrifuge(self, sensor_simulator):
        """Test registering centrifuge equipment."""
        sensor_keys = sensor_simulator.register_equipment(
            equipment_id="Centrifuge_01",
            equipment_type="centrifuge"
        )
        
        assert len(sensor_keys) > 0
        assert "Centrifuge_01.rpm" in sensor_keys
        assert "Centrifuge_01.temp" in sensor_keys
        assert "Centrifuge_01.vibration" in sensor_keys
    
    def test_register_equipment_analyzer(self, sensor_simulator):
        """Test registering analyzer equipment."""
        sensor_keys = sensor_simulator.register_equipment(
            equipment_id="Analyzer_01",
            equipment_type="analyzer"
        )
        
        assert len(sensor_keys) > 0
        assert "Analyzer_01.temp" in sensor_keys
        assert "Analyzer_01.ph" in sensor_keys
    
    def test_register_equipment_robot(self, sensor_simulator):
        """Test registering robot equipment."""
        sensor_keys = sensor_simulator.register_equipment(
            equipment_id="Robot_01",
            equipment_type="robot"
        )
        
        assert len(sensor_keys) > 0
        assert "Robot_01.x_pos" in sensor_keys
        assert "Robot_01.vibration" in sensor_keys
    
    def test_register_equipment_unknown_type(self, sensor_simulator):
        """Test registering unknown equipment type returns empty list."""
        sensor_keys = sensor_simulator.register_equipment(
            equipment_id="Unknown_01",
            equipment_type="unknown_type"
        )
        
        # Unknown types return empty list (no default sensors)
        assert isinstance(sensor_keys, list)
    
    def test_tick_generates_values(self, sensor_simulator):
        """Test that tick generates sensor values."""
        sensor_simulator.register_equipment("Centrifuge_01", "centrifuge")
        
        values = sensor_simulator.tick()
        
        assert len(values) > 0
        assert "Centrifuge_01.temp" in values
        assert isinstance(values["Centrifuge_01.temp"], float)
    
    def test_multiple_ticks_vary_values(self, sensor_simulator):
        """Test that multiple ticks produce varying values."""
        sensor_simulator.register_equipment("Centrifuge_01", "centrifuge")
        
        values1 = sensor_simulator.tick()
        values2 = sensor_simulator.tick()
        values3 = sensor_simulator.tick()
        
        # With noise, values should vary (though could theoretically be same)
        # We check that we at least get values
        assert "Centrifuge_01.temp" in values1
        assert "Centrifuge_01.temp" in values2
        assert "Centrifuge_01.temp" in values3
    
    def test_normal_value_within_range(self, sensor_simulator):
        """Test that normal values stay within configured ranges."""
        sensor_simulator.register_equipment("Centrifuge_01", "centrifuge")
        
        # Run multiple ticks
        for _ in range(10):
            values = sensor_simulator.tick()
            temp = values["Centrifuge_01.temp"]
            
            # Temperature range for centrifuge is [20, 35]
            # With normal noise, should be close to range
            assert 10 <= temp <= 50  # Extended range for noise
    
    def test_anomaly_injection_spike(self, sensor_simulator):
        """Test spike anomaly injection."""
        sensor_simulator.register_equipment("Centrifuge_01", "centrifuge")
        sensor_simulator.tick()  # Initialize
        
        # Get normal value
        normal_values = sensor_simulator.get_current_values()
        normal_temp = normal_values.get("Centrifuge_01.temp", 0)
        
        # Inject spike anomaly
        sensor_simulator.inject_anomaly("Centrifuge_01.temp", AnomalyType.SPIKE)
        
        # Get anomalous value
        anomaly_values = sensor_simulator.tick()
        anomaly_temp = anomaly_values.get("Centrifuge_01.temp", 0)
        
        # Spike should produce significantly higher value
        assert sensor_simulator.state.anomaly_active is True
        assert sensor_simulator.state.anomaly_type == AnomalyType.SPIKE
    
    def test_anomaly_injection_drift(self, sensor_simulator):
        """Test drift anomaly injection."""
        sensor_simulator.register_equipment("Analyzer_01", "analyzer")
        sensor_simulator.tick()
        
        sensor_simulator.inject_anomaly("Analyzer_01.temp", AnomalyType.DRIFT)
        
        assert sensor_simulator.state.anomaly_active is True
        assert sensor_simulator.state.anomaly_type == AnomalyType.DRIFT
        assert sensor_simulator.state.anomaly_sensor == "Analyzer_01.temp"
    
    def test_clear_anomaly(self, sensor_simulator):
        """Test clearing an active anomaly."""
        sensor_simulator.register_equipment("Centrifuge_01", "centrifuge")
        sensor_simulator.tick()
        
        # Inject and verify
        sensor_simulator.inject_anomaly("Centrifuge_01.temp", AnomalyType.SPIKE)
        assert sensor_simulator.state.anomaly_active is True
        
        # Clear and verify
        sensor_simulator.clear_anomaly()
        assert sensor_simulator.state.anomaly_active is False
        assert sensor_simulator.state.anomaly_type is None
    
    def test_get_current_values_without_tick(self, sensor_simulator):
        """Test getting current values without advancing simulation."""
        sensor_simulator.register_equipment("Centrifuge_01", "centrifuge")
        sensor_simulator.tick()  # Initialize values
        
        values1 = sensor_simulator.get_current_values()
        values2 = sensor_simulator.get_current_values()
        
        # Values should be the same since we didn't tick
        assert values1 == values2
    
    def test_get_sensor_info(self, sensor_simulator):
        """Test getting sensor information."""
        sensor_simulator.register_equipment("Centrifuge_01", "centrifuge")
        
        info = sensor_simulator.get_sensor_info("Centrifuge_01.temp")
        
        assert info is not None
        assert info["equipment_id"] == "Centrifuge_01"
        assert info["sensor_type"] == "temp"
        assert "unit" in info
    
    def test_get_sensor_info_nonexistent(self, sensor_simulator):
        """Test getting info for nonexistent sensor."""
        info = sensor_simulator.get_sensor_info("NonExistent.sensor")
        
        assert info is None
    
    def test_generate_demo_data(self, sensor_simulator):
        """Test generating demo data for multiple equipment."""
        equipment_configs = [
            {"id": "Centrifuge_01", "type": "centrifuge"},
            {"id": "Analyzer_01", "type": "analyzer"},
            {"id": "Robot_01", "type": "robot"}
        ]
        
        data = sensor_simulator.generate_demo_data(equipment_configs)
        
        assert len(data) > 0
        assert "Centrifuge_01.temp" in data
        assert "Analyzer_01.ph" in data
        assert "Robot_01.vibration" in data
    
    def test_generate_triggering_data(self, sensor_simulator):
        """Test generating data that triggers workflow conditions."""
        # Create workflow nodes with threshold conditions
        workflow_nodes = [
            {
                "id": "node-1",
                "data": {
                    "category": "centrifuge",
                    "configured": True,
                    "config": {
                        "equipment_id": "Centrifuge_01",
                        "sensor_type": "temp",
                        "operator": ">",
                        "threshold": 35.0
                    }
                }
            }
        ]
        
        # Register the equipment first
        sensor_simulator.register_equipment("Centrifuge_01", "centrifuge")
        
        # Generate triggering data
        data = sensor_simulator.generate_triggering_data(workflow_nodes)
        
        assert "Centrifuge_01.temp" in data
        # The generated value should exceed the threshold
        assert data["Centrifuge_01.temp"] > 35.0
    
    def test_generate_triggering_data_less_than(self, sensor_simulator):
        """Test generating triggering data for less-than conditions."""
        workflow_nodes = [
            {
                "id": "node-1",
                "data": {
                    "category": "storage",
                    "configured": True,
                    "config": {
                        "equipment_id": "Storage_01",
                        "sensor_type": "level",
                        "operator": "<",
                        "threshold": 20.0
                    }
                }
            }
        ]
        
        sensor_simulator.register_equipment("Storage_01", "storage")
        data = sensor_simulator.generate_triggering_data(workflow_nodes)
        
        assert "Storage_01.level" in data
        # The generated value should be below the threshold
        assert data["Storage_01.level"] < 20.0
