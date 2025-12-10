// src/services/openaiClient.js
// OpenAI API client for chat streaming

const OPENAI_API_KEY = import.meta.env.VITE_OPENAI_API_KEY;
const OPENAI_MODEL = import.meta.env.VITE_OPENAI_MODEL || 'gpt-4o-mini';

// System prompt for Nexus AI
export const SYSTEM_PROMPT = `You are Nexus AI, an intelligent assistant for an industrial pharmaceutical manufacturing facility.

## Your Role
You help operators monitor equipment, understand sensor data, create automation workflows, and respond to alerts.

## Capabilities
You can help with:
1. **Equipment status** - List and check equipment health
2. **Sensor readings** - Understand sensor data
3. **Alerts** - View and explain alerts
4. **Dependencies** - Understand equipment relationships
5. **Workflows** - Help create automation workflows
6. **Logs** - Review execution history

## Guidelines
- Be concise but informative
- Use technical terminology appropriate for manufacturing operators
- When creating workflows, always explain what the workflow will do
- For critical actions, confirm with the user first
- Provide actionable insights when reporting equipment status

## Response Format
- Use markdown formatting for readability
- Use bullet points for lists
- Highlight important values like temperatures, pressures, and percentages

## Context
The facility contains pharmaceutical manufacturing equipment including:
- Centrifuges
- Analyzers (chemical, spectral)
- Robots (cartesian, articulated)
- Storage tanks
- Conveyors
- Mixers
- Pumps

Each equipment has sensors for temperature, pressure, vibration, speed, etc.`;

/**
 * Check if API key is configured.
 * 
 * @returns {boolean}
 */
export function isApiKeyConfigured() {
    return Boolean(OPENAI_API_KEY);
}

/**
 * Build messages array for OpenAI API.
 * 
 * @param {Array} history - Chat history [{role, content}]
 * @param {string} newMessage - New user message
 * @returns {Array} Messages for API
 */
export function buildMessages(history, newMessage) {
    const messages = [
        { role: 'system', content: SYSTEM_PROMPT },
    ];

    // Add recent history (last 10 messages)
    const recentHistory = history.slice(-10);
    for (const msg of recentHistory) {
        if (msg.role === 'user' || msg.role === 'assistant') {
            messages.push({
                role: msg.role,
                content: msg.content,
            });
        }
    }

    // Add new message
    messages.push({ role: 'user', content: newMessage });

    return messages;
}

/**
 * Stream chat completion from OpenAI.
 * 
 * @param {Array} messages - Messages array for API
 * @param {Function} onChunk - Callback for each chunk (content string)
 * @param {Function} onError - Callback for errors
 * @param {Function} onComplete - Callback when done
 */
export async function streamChat(messages, onChunk, onError, onComplete) {
    if (!OPENAI_API_KEY) {
        onError(new Error('OpenAI API key not configured. Add VITE_OPENAI_API_KEY to your .env file.'));
        return;
    }

    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${OPENAI_API_KEY}`,
            },
            body: JSON.stringify({
                model: OPENAI_MODEL,
                messages,
                stream: true,
                temperature: 0.3,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error?.message || `API error: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                onComplete();
                break;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') {
                        onComplete();
                        return;
                    }

                    try {
                        const json = JSON.parse(data);
                        const content = json.choices?.[0]?.delta?.content;
                        if (content) {
                            onChunk(content);
                        }
                    } catch (e) {
                        // Ignore JSON parse errors for incomplete chunks
                    }
                }
            }
        }
    } catch (error) {
        onError(error);
    }
}

/**
 * Non-streaming chat completion (simpler, for tool-like responses).
 * 
 * @param {Array} messages - Messages array for API
 * @returns {Promise<string>} Response content
 */
export async function chat(messages) {
    if (!OPENAI_API_KEY) {
        throw new Error('OpenAI API key not configured. Add VITE_OPENAI_API_KEY to your .env file.');
    }

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${OPENAI_API_KEY}`,
        },
        body: JSON.stringify({
            model: OPENAI_MODEL,
            messages,
            temperature: 0.3,
        }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error?.message || `API error: ${response.status}`);
    }

    const data = await response.json();
    return data.choices[0]?.message?.content || '';
}

const openaiClient = {
    isApiKeyConfigured,
    buildMessages,
    streamChat,
    chat,
    SYSTEM_PROMPT,
};

export default openaiClient;
