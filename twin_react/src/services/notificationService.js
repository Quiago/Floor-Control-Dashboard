// src/services/notificationService.js
// Notification service (mock mode for frontend)

/**
 * Notification result object
 */
class NotificationResult {
    constructor(success, channel, recipient, messageId = null, error = null) {
        this.success = success;
        this.channel = channel;
        this.recipient = recipient;
        this.message_id = messageId;
        this.error = error;
        this.timestamp = new Date().toISOString();
    }
}

/**
 * Mock notification - logs to console instead of sending.
 * 
 * @param {string} channel - 'whatsapp' | 'email' | 'webhook'
 * @param {string} recipient - Phone number, email, or URL
 * @param {string} message - Message content
 * @returns {NotificationResult}
 */
function mockNotification(channel, recipient, message) {
    console.log(`[MOCK ${channel.toUpperCase()}] To: ${recipient}`);
    console.log(`[MOCK ${channel.toUpperCase()}] Message: ${message.slice(0, 100)}...`);

    return new NotificationResult(
        true,
        channel,
        recipient,
        `mock_${channel}_${Date.now()}`
    );
}

/**
 * Send WhatsApp message (mock).
 * 
 * @param {string} phoneNumber - Recipient phone number
 * @param {string} message - Message text
 * @returns {Promise<NotificationResult>}
 */
export async function sendWhatsApp(phoneNumber, message) {
    // In production, this would call the WhatsApp Business API
    return mockNotification('whatsapp', phoneNumber, message);
}

/**
 * Send email (mock).
 * 
 * @param {string} email - Recipient email
 * @param {string} subject - Email subject
 * @param {string} body - Email body
 * @returns {Promise<NotificationResult>}
 */
export async function sendEmail(email, subject, body) {
    // In production, this would call an email API
    return mockNotification('email', email, `${subject}: ${body}`);
}

/**
 * Send webhook (mock).
 * 
 * @param {string} url - Webhook URL
 * @param {Object} payload - JSON payload
 * @returns {Promise<NotificationResult>}
 */
export async function sendWebhook(url, payload) {
    // In production, this would make an HTTP POST request
    return mockNotification('webhook', url, JSON.stringify(payload));
}

/**
 * Generate alert message content.
 * 
 * @param {Object} options - Alert options
 * @returns {Object} { text, html, subject }
 */
export function createThresholdAlert({
    equipmentName,
    sensor,
    value,
    threshold,
    unit = '',
    severity = 'warning',
}) {
    const emoji = severity === 'critical' ? '🔴' : severity === 'warning' ? '🟡' : '🟢';
    const now = new Date().toLocaleString();

    const text = `${emoji} NEXUS ALERT - ${severity.toUpperCase()}

Equipment: ${equipmentName}
Sensor: ${sensor}
Current Value: ${value} ${unit}
Threshold: ${threshold} ${unit}
Time: ${now}`;

    const html = `
    <div style="font-family: Arial, sans-serif; padding: 20px; background: #1a1a2e; color: white;">
      <h2 style="color: ${severity === 'critical' ? '#ef4444' : '#eab308'};">
        ${emoji} NEXUS ALERT - ${severity.toUpperCase()}
      </h2>
      <table style="margin: 20px 0;">
        <tr><td style="padding: 5px; color: #9ca3af;">Equipment:</td><td style="padding: 5px;">${equipmentName}</td></tr>
        <tr><td style="padding: 5px; color: #9ca3af;">Sensor:</td><td style="padding: 5px;">${sensor}</td></tr>
        <tr><td style="padding: 5px; color: #9ca3af;">Current Value:</td><td style="padding: 5px; color: #ef4444;">${value} ${unit}</td></tr>
        <tr><td style="padding: 5px; color: #9ca3af;">Threshold:</td><td style="padding: 5px;">${threshold} ${unit}</td></tr>
        <tr><td style="padding: 5px; color: #9ca3af;">Time:</td><td style="padding: 5px;">${now}</td></tr>
      </table>
      <p style="color: #6b7280; font-size: 12px;">Sent by Nexus Monitoring System</p>
    </div>
  `;

    return {
        text,
        html,
        subject: `[${severity.toUpperCase()}] ${equipmentName} - ${sensor} Alert`,
    };
}

/**
 * Send alert via specified channel.
 * 
 * @param {string} channel - 'whatsapp' | 'email' | 'webhook'
 * @param {string} recipient - Target recipient
 * @param {string} message - Alert message
 * @param {Object} options - Additional options
 * @returns {Promise<NotificationResult>}
 */
export async function sendAlert(channel, recipient, message, options = {}) {
    switch (channel.toLowerCase()) {
        case 'whatsapp':
            return sendWhatsApp(recipient, message);
        case 'email':
            return sendEmail(recipient, options.subject || 'Nexus Alert', message);
        case 'webhook':
            return sendWebhook(recipient, options.payload || { message, recipient });
        default:
            return new NotificationResult(false, channel, recipient, null, `Unknown channel: ${channel}`);
    }
}

const notificationService = {
    sendWhatsApp,
    sendEmail,
    sendWebhook,
    sendAlert,
    createThresholdAlert,
};

export default notificationService;
