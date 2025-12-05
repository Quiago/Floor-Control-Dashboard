# app/services/notification_service.py
"""
Notification Service for WhatsApp and Email alerts.

Handles sending notifications through various channels:
- WhatsApp Business API (Meta)
- Gmail API / SMTP
- Webhooks (for extensibility)
"""
import os
import json
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import asyncio


class NotificationChannel(Enum):
    """Supported notification channels."""
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"


@dataclass
class NotificationResult:
    """Result of a notification attempt."""
    success: bool
    channel: str
    recipient: str
    message_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            'success': self.success,
            'channel': self.channel,
            'recipient': self.recipient,
            'message_id': self.message_id,
            'error': self.error,
            'timestamp': self.timestamp
        }


class NotificationConfig:
    """
    Configuration for notification services.
    
    Load from environment variables or .env file.
    For demo, supports mock mode when credentials not configured.
    """
    
    def __init__(self):
        # WhatsApp Business API (Meta)
        self.whatsapp_phone_id = os.getenv('WHATSAPP_PHONE_ID', '')
        self.whatsapp_token = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
        self.whatsapp_api_version = os.getenv('WHATSAPP_API_VERSION', 'v18.0')
        
        # Email (Gmail SMTP or API)
        self.email_smtp_host = os.getenv('EMAIL_SMTP_HOST', 'smtp.gmail.com')
        self.email_smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.email_username = os.getenv('EMAIL_USERNAME', '')
        self.email_password = os.getenv('EMAIL_APP_PASSWORD', '')  # App password for Gmail
        self.email_from_name = os.getenv('EMAIL_FROM_NAME', 'Nexus Alert System')
        
        # Webhook
        self.webhook_url = os.getenv('WEBHOOK_URL', '')
        self.webhook_secret = os.getenv('WEBHOOK_SECRET', '')
        
        # Demo/Mock mode
        self.mock_mode = os.getenv('NOTIFICATION_MOCK_MODE', 'true').lower() == 'true'
    
    @property
    def whatsapp_configured(self) -> bool:
        return bool(self.whatsapp_phone_id and self.whatsapp_token)
    
    @property
    def email_configured(self) -> bool:
        return bool(self.email_username and self.email_password)
    
    @property
    def webhook_configured(self) -> bool:
        return bool(self.webhook_url)


class NotificationService:
    """
    Service for sending notifications across multiple channels.
    
    Supports:
    - WhatsApp Business API
    - Email via SMTP
    - Generic webhooks
    
    In mock mode, logs notifications without actually sending them.
    """
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        self.config = config or NotificationConfig()
        self._http_client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client
    
    async def close(self):
        """Close the HTTP client."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
    
    # --- WHATSAPP ---
    
    async def send_whatsapp(self, phone_number: str, message: str, 
                           template_name: Optional[str] = None) -> NotificationResult:
        """
        Send WhatsApp message via Meta Business API.
        
        Args:
            phone_number: Recipient phone number with country code (e.g., +1234567890)
            message: Message text (for non-template messages)
            template_name: Optional template name for pre-approved messages
        """
        if self.config.mock_mode or not self.config.whatsapp_configured:
            return self._mock_notification(NotificationChannel.WHATSAPP, phone_number, message)
        
        try:
            client = await self._get_client()
            url = f"https://graph.facebook.com/{self.config.whatsapp_api_version}/{self.config.whatsapp_phone_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.config.whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            # Clean phone number (remove + and spaces)
            clean_phone = phone_number.replace("+", "").replace(" ", "").replace("-", "")
            
            if template_name:
                # Template message (for business-initiated conversations)
                payload = {
                    "messaging_product": "whatsapp",
                    "to": clean_phone,
                    "type": "template",
                    "template": {
                        "name": template_name,
                        "language": {"code": "en"}
                    }
                }
            else:
                # Text message (requires 24-hour conversation window)
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": clean_phone,
                    "type": "text",
                    "text": {"body": message}
                }
            
            response = await client.post(url, headers=headers, json=payload)
            response_data = response.json()
            
            if response.status_code == 200:
                message_id = response_data.get('messages', [{}])[0].get('id')
                return NotificationResult(
                    success=True,
                    channel=NotificationChannel.WHATSAPP.value,
                    recipient=phone_number,
                    message_id=message_id
                )
            else:
                error = response_data.get('error', {}).get('message', 'Unknown error')
                return NotificationResult(
                    success=False,
                    channel=NotificationChannel.WHATSAPP.value,
                    recipient=phone_number,
                    error=f"API Error: {error}"
                )
                
        except Exception as e:
            return NotificationResult(
                success=False,
                channel=NotificationChannel.WHATSAPP.value,
                recipient=phone_number,
                error=str(e)
            )
    
    # --- EMAIL ---
    
    async def send_email(self, to_email: str, subject: str, body: str,
                        html_body: Optional[str] = None) -> NotificationResult:
        """
        Send email via SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
        """
        if self.config.mock_mode or not self.config.email_configured:
            return self._mock_notification(NotificationChannel.EMAIL, to_email, f"{subject}: {body}")
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.email_from_name} <{self.config.email_username}>"
            msg['To'] = to_email
            
            # Add plain text part
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML part if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Send via SMTP (run in thread pool to not block)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_smtp, msg)
            
            return NotificationResult(
                success=True,
                channel=NotificationChannel.EMAIL.value,
                recipient=to_email,
                message_id=f"email_{datetime.now().timestamp()}"
            )
            
        except Exception as e:
            return NotificationResult(
                success=False,
                channel=NotificationChannel.EMAIL.value,
                recipient=to_email,
                error=str(e)
            )
    
    def _send_smtp(self, msg: MIMEMultipart):
        """Send email via SMTP (blocking, run in thread pool)."""
        with smtplib.SMTP(self.config.email_smtp_host, self.config.email_smtp_port) as server:
            server.starttls()
            server.login(self.config.email_username, self.config.email_password)
            server.send_message(msg)
    
    # --- WEBHOOK ---
    
    async def send_webhook(self, url: Optional[str], payload: Dict) -> NotificationResult:
        """
        Send webhook notification.
        
        Args:
            url: Webhook URL (uses config URL if not provided)
            payload: JSON payload to send
        """
        webhook_url = url or self.config.webhook_url
        
        if self.config.mock_mode or not webhook_url:
            return self._mock_notification(
                NotificationChannel.WEBHOOK, 
                webhook_url or "no_url", 
                json.dumps(payload)
            )
        
        try:
            client = await self._get_client()
            
            headers = {"Content-Type": "application/json"}
            if self.config.webhook_secret:
                headers["X-Webhook-Secret"] = self.config.webhook_secret
            
            response = await client.post(webhook_url, headers=headers, json=payload)
            
            if response.status_code in (200, 201, 202, 204):
                return NotificationResult(
                    success=True,
                    channel=NotificationChannel.WEBHOOK.value,
                    recipient=webhook_url,
                    message_id=f"webhook_{datetime.now().timestamp()}"
                )
            else:
                return NotificationResult(
                    success=False,
                    channel=NotificationChannel.WEBHOOK.value,
                    recipient=webhook_url,
                    error=f"HTTP {response.status_code}: {response.text[:200]}"
                )
                
        except Exception as e:
            return NotificationResult(
                success=False,
                channel=NotificationChannel.WEBHOOK.value,
                recipient=webhook_url or "no_url",
                error=str(e)
            )
    
    # --- HELPERS ---
    
    def _mock_notification(self, channel: NotificationChannel, 
                          recipient: str, message: str) -> NotificationResult:
        """Mock notification for demo/testing."""
        print(f"[MOCK {channel.value.upper()}] To: {recipient}")
        print(f"[MOCK {channel.value.upper()}] Message: {message[:100]}...")
        
        return NotificationResult(
            success=True,
            channel=channel.value,
            recipient=recipient,
            message_id=f"mock_{channel.value}_{datetime.now().timestamp()}"
        )
    
    # --- CONVENIENCE METHODS ---
    
    async def send_alert(self, channel: str, recipient: str, 
                        message: str, **kwargs) -> NotificationResult:
        """
        Send alert via specified channel.
        
        Args:
            channel: 'whatsapp', 'email', or 'webhook'
            recipient: Phone number, email, or webhook URL
            message: Alert message
            **kwargs: Additional channel-specific parameters
        """
        channel_lower = channel.lower()
        
        if channel_lower == NotificationChannel.WHATSAPP.value:
            return await self.send_whatsapp(recipient, message, 
                                           template_name=kwargs.get('template_name'))
        
        elif channel_lower == NotificationChannel.EMAIL.value:
            subject = kwargs.get('subject', 'Nexus Alert')
            return await self.send_email(recipient, subject, message,
                                        html_body=kwargs.get('html_body'))
        
        elif channel_lower == NotificationChannel.WEBHOOK.value:
            payload = kwargs.get('payload', {'message': message, 'recipient': recipient})
            return await self.send_webhook(recipient, payload)
        
        else:
            return NotificationResult(
                success=False,
                channel=channel,
                recipient=recipient,
                error=f"Unknown channel: {channel}"
            )


# --- MESSAGE TEMPLATES ---

class AlertTemplates:
    """Pre-defined alert message templates."""
    
    @staticmethod
    def threshold_alert(equipment_name: str, sensor: str, value: float, 
                       threshold: float, unit: str, severity: str = "warning") -> Dict[str, str]:
        """Generate threshold alert message."""
        emoji = "🔴" if severity == "critical" else "🟡" if severity == "warning" else "🟢"
        
        text = (
            f"{emoji} NEXUS ALERT - {severity.upper()}\n\n"
            f"Equipment: {equipment_name}\n"
            f"Sensor: {sensor}\n"
            f"Current Value: {value} {unit}\n"
            f"Threshold: {threshold} {unit}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; background: #1a1a2e; color: white;">
            <h2 style="color: {'#ef4444' if severity == 'critical' else '#eab308'};">
                {emoji} NEXUS ALERT - {severity.upper()}
            </h2>
            <table style="margin: 20px 0;">
                <tr><td style="padding: 5px; color: #9ca3af;">Equipment:</td><td style="padding: 5px;">{equipment_name}</td></tr>
                <tr><td style="padding: 5px; color: #9ca3af;">Sensor:</td><td style="padding: 5px;">{sensor}</td></tr>
                <tr><td style="padding: 5px; color: #9ca3af;">Current Value:</td><td style="padding: 5px; color: #ef4444;">{value} {unit}</td></tr>
                <tr><td style="padding: 5px; color: #9ca3af;">Threshold:</td><td style="padding: 5px;">{threshold} {unit}</td></tr>
                <tr><td style="padding: 5px; color: #9ca3af;">Time:</td><td style="padding: 5px;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
            </table>
            <p style="color: #6b7280; font-size: 12px;">Sent by Nexus Monitoring System</p>
        </div>
        """
        
        return {
            'text': text,
            'html': html,
            'subject': f"[{severity.upper()}] {equipment_name} - {sensor} Alert"
        }
    
    @staticmethod
    def equipment_status_change(equipment_name: str, old_status: str, 
                               new_status: str, reason: str = "") -> Dict[str, str]:
        """Generate equipment status change message."""
        emoji = "🔴" if new_status == "critical" else "🟡" if new_status == "warning" else "🟢"
        
        text = (
            f"{emoji} EQUIPMENT STATUS CHANGE\n\n"
            f"Equipment: {equipment_name}\n"
            f"Previous Status: {old_status}\n"
            f"New Status: {new_status}\n"
            f"{'Reason: ' + reason if reason else ''}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return {
            'text': text,
            'subject': f"[STATUS] {equipment_name} changed to {new_status}"
        }


# Global instance
notification_service = NotificationService()

