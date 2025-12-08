# tests/test_glb_parser.py
"""Unit tests for GLB parser and equipment extraction."""
import pytest
from pathlib import Path


class TestEquipmentClassification:
    """Tests for equipment type classification."""
    
    def test_classify_equipment_analyzer(self):
        """Test classification of analyzer equipment."""
        from app.extractors.glb_parser import _classify_equipment
        
        assert _classify_equipment("Chemical_Analyzer_01") == "analyzer"
        assert _classify_equipment("ANALYZER_MAIN") == "analyzer"
        assert _classify_equipment("analyzer") == "analyzer"
    
    def test_classify_equipment_robot(self):
        """Test classification of robot/cartesian equipment."""
        from app.extractors.glb_parser import _classify_equipment
        
        assert _classify_equipment("Cartesian_Robot_01") == "robot"
        assert _classify_equipment("CARTESIAN_ARM") == "robot"
    
    def test_classify_equipment_centrifuge(self):
        """Test classification of centrifuge equipment."""
        from app.extractors.glb_parser import _classify_equipment
        
        assert _classify_equipment("Centrifuge_01") == "centrifuge"
        assert _classify_equipment("CENTRIFUGE_MAIN") == "centrifuge"
    
    def test_classify_equipment_storage(self):
        """Test classification of storage equipment."""
        from app.extractors.glb_parser import _classify_equipment
        
        assert _classify_equipment("Storage_Tank_01") == "storage"
        assert _classify_equipment("STORAGE_UNIT") == "storage"
    
    def test_classify_equipment_conveyor(self):
        """Test classification of conveyor equipment."""
        from app.extractors.glb_parser import _classify_equipment
        
        assert _classify_equipment("Conveyor_Belt_A") == "conveyor"
        assert _classify_equipment("CONVEYOR_MAIN") == "conveyor"
    
    def test_classify_equipment_mixer(self):
        """Test classification of mixer equipment."""
        from app.extractors.glb_parser import _classify_equipment
        
        assert _classify_equipment("Mixer_01") == "mixer"
        assert _classify_equipment("INDUSTRIAL_MIXER") == "mixer"
    
    def test_classify_equipment_pump(self):
        """Test classification of pump equipment."""
        from app.extractors.glb_parser import _classify_equipment
        
        assert _classify_equipment("Pump_01") == "pump"
        assert _classify_equipment("VACUUM_PUMP") == "pump"
    
    def test_classify_equipment_unknown(self):
        """Test classification of unknown equipment."""
        from app.extractors.glb_parser import _classify_equipment
        
        assert _classify_equipment("SomeRandomName") == "unknown"
        assert _classify_equipment("XYZ_123") == "unknown"


class TestSensorDefinitions:
    """Tests for sensor definitions by equipment type."""
    
    def test_get_sensors_for_analyzer(self):
        """Test sensor definitions for analyzer."""
        from app.extractors.glb_parser import get_sensors_for_type
        
        sensors = get_sensors_for_type("analyzer")
        
        assert len(sensors) > 0
        sensor_ids = [s["id"] for s in sensors]
        assert "temp" in sensor_ids
        assert "ph" in sensor_ids
        assert "turbidity" in sensor_ids
    
    def test_get_sensors_for_robot(self):
        """Test sensor definitions for robot."""
        from app.extractors.glb_parser import get_sensors_for_type
        
        sensors = get_sensors_for_type("robot")
        
        assert len(sensors) > 0
        sensor_ids = [s["id"] for s in sensors]
        assert "x_pos" in sensor_ids
        assert "y_pos" in sensor_ids
        assert "vibration" in sensor_ids
        assert "current" in sensor_ids
    
    def test_get_sensors_for_centrifuge(self):
        """Test sensor definitions for centrifuge."""
        from app.extractors.glb_parser import get_sensors_for_type
        
        sensors = get_sensors_for_type("centrifuge")
        
        assert len(sensors) > 0
        sensor_ids = [s["id"] for s in sensors]
        assert "rpm" in sensor_ids
        assert "vibration" in sensor_ids
        assert "temp" in sensor_ids
    
    def test_get_sensors_for_storage(self):
        """Test sensor definitions for storage."""
        from app.extractors.glb_parser import get_sensors_for_type
        
        sensors = get_sensors_for_type("storage")
        
        assert len(sensors) > 0
        sensor_ids = [s["id"] for s in sensors]
        assert "level" in sensor_ids
        assert "temp" in sensor_ids
        assert "humidity" in sensor_ids
    
    def test_get_sensors_for_conveyor(self):
        """Test sensor definitions for conveyor."""
        from app.extractors.glb_parser import get_sensors_for_type
        
        sensors = get_sensors_for_type("conveyor")
        
        assert len(sensors) > 0
        sensor_ids = [s["id"] for s in sensors]
        assert "speed" in sensor_ids
        assert "current" in sensor_ids
        assert "vibration" in sensor_ids
    
    def test_get_sensors_for_unknown_type(self):
        """Test default sensor definitions for unknown type."""
        from app.extractors.glb_parser import get_sensors_for_type
        
        sensors = get_sensors_for_type("unknown_type")
        
        # Should get at least a temperature sensor
        assert len(sensors) > 0
        sensor_ids = [s["id"] for s in sensors]
        assert "temp" in sensor_ids
    
    def test_sensor_structure(self):
        """Test that sensor definitions have correct structure."""
        from app.extractors.glb_parser import get_sensors_for_type
        
        sensors = get_sensors_for_type("centrifuge")
        
        for sensor in sensors:
            assert "id" in sensor
            assert "name" in sensor
            assert "unit" in sensor
            assert "range" in sensor
            assert isinstance(sensor["range"], list)
            assert len(sensor["range"]) == 2


class TestGLBParsing:
    """Tests for GLB file parsing."""
    
    def test_load_equipment_from_glb_with_existing_file(self):
        """Test loading equipment from actual GLB file if it exists."""
        from app.extractors.glb_parser import load_equipment_from_glb
        
        glb_path = "assets/pharmaceutical_manufacturing_machinery.glb"
        
        if Path(glb_path).exists():
            equipment = load_equipment_from_glb(glb_path)
            
            assert isinstance(equipment, list)
            
            if len(equipment) > 0:
                # Check structure of equipment items
                for eq in equipment:
                    assert "id" in eq
                    assert "name" in eq
                    assert "type" in eq
                    assert "sensors" in eq
                    assert "label" in eq
        else:
            pytest.skip("GLB file not found, skipping test")
    
    def test_load_equipment_from_nonexistent_file(self):
        """Test loading equipment from nonexistent file returns empty list."""
        from app.extractors.glb_parser import load_equipment_from_glb
        
        equipment = load_equipment_from_glb("nonexistent/path/model.glb")
        
        assert equipment == []
    
    def test_parse_glb_invalid_file(self):
        """Test parsing invalid GLB file raises error."""
        from app.extractors.glb_parser import parse_glb
        import tempfile
        import os
        
        # Create a temporary invalid file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.glb', delete=False) as f:
            f.write(b'invalid content')
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid GLB file"):
                parse_glb(temp_path)
        finally:
            os.unlink(temp_path)


class TestEquipmentEnrichment:
    """Tests for equipment data enrichment."""
    
    def test_equipment_label_generation(self):
        """Test that equipment labels are properly generated."""
        from app.extractors.glb_parser import load_equipment_from_glb
        
        glb_path = "assets/pharmaceutical_manufacturing_machinery.glb"
        
        if Path(glb_path).exists():
            equipment = load_equipment_from_glb(glb_path)
            
            for eq in equipment:
                # Label should be title case with spaces
                assert "_" not in eq["label"] or eq["label"].istitle()
        else:
            pytest.skip("GLB file not found, skipping test")
    
    def test_equipment_has_sensors(self):
        """Test that all equipment has sensor definitions."""
        from app.extractors.glb_parser import load_equipment_from_glb
        
        glb_path = "assets/pharmaceutical_manufacturing_machinery.glb"
        
        if Path(glb_path).exists():
            equipment = load_equipment_from_glb(glb_path)
            
            for eq in equipment:
                assert "sensors" in eq
                assert isinstance(eq["sensors"], list)
                assert len(eq["sensors"]) > 0
        else:
            pytest.skip("GLB file not found, skipping test")
