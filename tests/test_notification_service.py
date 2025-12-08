# tests/test_notification_service.py
"""Unit tests for NotificationService."""
import pytest
import asyncio
from unittest.mock import patch, MagicMock


class TestNotificationResult:
    """Tests for NotificationResult dataclass."""
    
    def test_notification_result_to_dict(self):
        """Test NotificationResult serialization."""
        from app.services.notification_service import NotificationResult
        
        result = NotificationResult(
            success=True,
            channel="whatsapp",
            recipient="+1234567890",
            message_id="msg-001",
            error=None
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["success"] is True
        assert result_dict["channel"] == "whatsapp"
        assert result_dict["recipient"] == "+1234567890"
        assert result_dict["message_id"] == "msg-001"
        assert result_dict["error"] is None
        assert "timestamp" in result_dict
    
    def test_notification_result_with_error(self):
        """Test NotificationResult with error."""
        from app.services.notification_service import NotificationResult
        
        result = NotificationResult(
            success=False,
            channel="email",
            recipient="test@example.com",
            error="SMTP connection failed"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["success"] is False
        assert result_dict["error"] == "SMTP connection failed"


class TestNotificationConfig:
    """Tests for NotificationConfig class."""
    
    def test_mock_mode_enabled(self, mock_notification_config):
        """Test that mock mode is properly enabled."""
        assert mock_notification_config.mock_mode is True
    
    def test_whatsapp_configured_property(self, mock_notification_config):
        """Test WhatsApp configuration detection."""
        # In mock mode without actual credentials
        # whatsapp_configured depends on env vars
        result = mock_notification_config.whatsapp_configured
        assert isinstance(result, bool)
    
    def test_email_configured_property(self, mock_notification_config):
        """Test email configuration detection."""
        result = mock_notification_config.email_configured
        assert isinstance(result, bool)


class TestNotificationService:
    """Tests for NotificationService class."""
    
    @pytest.mark.asyncio
    async def test_mock_whatsapp_notification(self, mock_notification_service):
        """Test WhatsApp notification in mock mode."""
        result = await mock_notification_service.send_whatsapp(
            phone_number="+1234567890",
            message="Test message from pytest"
        )
        
        assert result.success is True
        assert result.channel == "whatsapp"
        assert result.recipient == "+1234567890"
        assert "mock" in result.message_id.lower()
        
        await mock_notification_service.close()
    
    @pytest.mark.asyncio
    async def test_mock_email_notification(self, mock_notification_service):
        """Test email notification in mock mode."""
        result = await mock_notification_service.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            body="Test body content"
        )
        
        assert result.success is True
        assert result.channel == "email"
        assert result.recipient == "test@example.com"
        assert "mock" in result.message_id.lower()
        
        await mock_notification_service.close()
    
    @pytest.mark.asyncio
    async def test_mock_webhook_notification(self, mock_notification_service):
        """Test webhook notification in mock mode."""
        result = await mock_notification_service.send_webhook(
            url="https://api.example.com/webhook",
            payload={"event": "test", "data": {"value": 42}}
        )
        
        assert result.success is True
        assert result.channel == "webhook"
        assert "mock" in result.message_id.lower()
        
        await mock_notification_service.close()
    
    @pytest.mark.asyncio
    async def test_send_alert_whatsapp_routing(self, mock_notification_service):
        """Test that send_alert routes to WhatsApp correctly."""
        result = await mock_notification_service.send_alert(
            channel="whatsapp",
            recipient="+9876543210",
            message="Alert test"
        )
        
        assert result.success is True
        assert result.channel == "whatsapp"
        
        await mock_notification_service.close()
    
    @pytest.mark.asyncio
    async def test_send_alert_email_routing(self, mock_notification_service):
        """Test that send_alert routes to email correctly."""
        result = await mock_notification_service.send_alert(
            channel="email",
            recipient="alert@example.com",
            message="Email alert test",
            subject="Test Alert"
        )
        
        assert result.success is True
        assert result.channel == "email"
        
        await mock_notification_service.close()
    
    @pytest.mark.asyncio
    async def test_send_alert_webhook_routing(self, mock_notification_service):
        """Test that send_alert routes to webhook correctly."""
        result = await mock_notification_service.send_alert(
            channel="webhook",
            recipient="https://hooks.example.com/test",
            message="Webhook alert test"
        )
        
        assert result.success is True
        assert result.channel == "webhook"
        
        await mock_notification_service.close()
    
    @pytest.mark.asyncio
    async def test_send_alert_invalid_channel(self, mock_notification_service):
        """Test that send_alert handles invalid channel."""
        result = await mock_notification_service.send_alert(
            channel="invalid_channel",
            recipient="test",
            message="Test"
        )
        
        assert result.success is False
        assert "Unknown channel" in result.error or "unsupported" in result.error.lower()
        
        await mock_notification_service.close()


class TestAlertTemplates:
    """Tests for AlertTemplates class."""
    
    def test_threshold_alert_warning(self):
        """Test threshold alert template generation."""
        from app.services.notification_service import AlertTemplates
        
        result = AlertTemplates.threshold_alert(
            equipment_name="Centrifuge_01",
            sensor="Temperature",
            value=45.5,
            threshold=35.0,
            unit="°C",
            severity="warning"
        )
        
        # Result is a dict with 'text', 'html', and 'subject' keys
        assert isinstance(result, dict)
        assert "text" in result
        assert "Centrifuge_01" in result["text"]
        assert "Temperature" in result["text"]
        assert "45.5" in result["text"]
        assert "35.0" in result["text"]
        assert "°C" in result["text"]
    
    def test_threshold_alert_critical(self):
        """Test critical threshold alert template."""
        from app.services.notification_service import AlertTemplates
        
        result = AlertTemplates.threshold_alert(
            equipment_name="Pump_01",
            sensor="Pressure",
            value=300.0,
            threshold=250.0,
            unit="PSI",
            severity="critical"
        )
        
        assert isinstance(result, dict)
        assert "Pump_01" in result["text"]
        assert "CRITICAL" in result["text"]
    
    def test_equipment_status_change(self):
        """Test equipment status change template."""
        from app.services.notification_service import AlertTemplates
        
        result = AlertTemplates.equipment_status_change(
            equipment_name="Analyzer_01",
            old_status="Running",
            new_status="Stopped",
            reason="Maintenance scheduled"
        )
        
        assert isinstance(result, dict)
        assert "text" in result
        assert "Analyzer_01" in result["text"]
        assert "Running" in result["text"]
        assert "Stopped" in result["text"]

