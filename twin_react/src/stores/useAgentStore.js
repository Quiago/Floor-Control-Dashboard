// src/stores/useAgentStore.js
// State management for AI chat agent

import { create } from 'zustand';
import { buildMessages, isApiKeyConfigured, streamChat } from '../services/openaiClient';

const useAgentStore = create((set, get) => ({
    // === CHAT STATE ===
    chatHistory: [
        {
            role: 'assistant',
            content: `👋 Hello! I'm **Nexus AI**, your intelligent assistant for industrial monitoring.

I can help you with:
- 📊 **Equipment status** - Check any machine's health
- 📈 **Sensor readings** - View live sensor data
- ⚠️ **Alerts** - Review recent warnings
- 🔧 **Workflows** - Create automation rules from text

How can I help you today?`,
            time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        },
    ],
    chatInput: '',
    isThinking: false,
    errorMessage: '',

    // === STREAMING STATE ===
    streamingResponse: '',
    isStreaming: false,

    // === WORKFLOW APPROVAL STATE ===
    pendingWorkflow: null,
    awaitingApproval: false,

    // === ACTIONS ===

    setChatInput: (value) => set({ chatInput: value }),

    sendMessage: async (message = null) => {
        const { chatInput, chatHistory } = get();
        const messageText = message || chatInput;

        if (!messageText.trim()) return;

        // Clear input
        set({ chatInput: '' });

        // Add user message
        const now = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        const userMessage = {
            role: 'user',
            content: messageText,
            time: now,
        };

        // Add empty assistant message for streaming
        const assistantMessage = {
            role: 'assistant',
            content: '',
            time: now,
        };

        set({
            chatHistory: [...chatHistory, userMessage, assistantMessage],
            isThinking: true,
            isStreaming: true,
            streamingResponse: '',
            errorMessage: '',
        });

        // Check for API key
        if (!isApiKeyConfigured()) {
            set(state => ({
                chatHistory: state.chatHistory.map((msg, idx) =>
                    idx === state.chatHistory.length - 1
                        ? { ...msg, content: '⚠️ **OpenAI API Key not configured**\n\nPlease add `VITE_OPENAI_API_KEY=sk-...` to your `.env` file and restart the dev server.' }
                        : msg
                ),
                isThinking: false,
                isStreaming: false,
            }));
            return;
        }

        try {
            // Build messages for API
            const messages = buildMessages(chatHistory, messageText);

            // Stream response
            await streamChat(
                messages,
                // onChunk
                (chunk) => {
                    set(state => {
                        const newContent = state.streamingResponse + chunk;
                        return {
                            streamingResponse: newContent,
                            chatHistory: state.chatHistory.map((msg, idx) =>
                                idx === state.chatHistory.length - 1
                                    ? { ...msg, content: newContent }
                                    : msg
                            ),
                        };
                    });
                },
                // onError
                (error) => {
                    console.error('Chat error:', error);
                    set(state => ({
                        errorMessage: error.message,
                        chatHistory: state.chatHistory.map((msg, idx) =>
                            idx === state.chatHistory.length - 1
                                ? { ...msg, content: `⚠️ I encountered an error: ${error.message}` }
                                : msg
                        ),
                        isThinking: false,
                        isStreaming: false,
                    }));
                },
                // onComplete
                () => {
                    set({
                        isThinking: false,
                        isStreaming: false,
                        streamingResponse: '',
                    });

                    // Check for workflow creation keywords in response
                    const { chatHistory } = get();
                    const lastMessage = chatHistory[chatHistory.length - 1];
                    if (lastMessage?.content?.includes('workflow') &&
                        lastMessage?.content?.includes('approve') ||
                        lastMessage?.content?.includes('confirm')) {
                        // Could set awaitingApproval = true here if needed
                    }
                }
            );
        } catch (error) {
            console.error('Chat error:', error);
            set(state => ({
                errorMessage: error.message,
                chatHistory: state.chatHistory.map((msg, idx) =>
                    idx === state.chatHistory.length - 1
                        ? { ...msg, content: `⚠️ I encountered an error: ${error.message}` }
                        : msg
                ),
                isThinking: false,
                isStreaming: false,
            }));
        }
    },

    clearChat: () => {
        set({
            chatHistory: [
                {
                    role: 'assistant',
                    content: '🔄 Chat cleared. How can I help you?',
                    time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
                },
            ],
            pendingWorkflow: null,
            awaitingApproval: false,
            errorMessage: '',
            streamingResponse: '',
            isStreaming: false,
        });
    },

    approveWorkflow: async () => {
        const { pendingWorkflow } = get();

        if (!pendingWorkflow) return;

        set({ isThinking: true });

        // In a real implementation, this would save the workflow and start simulation
        const now = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

        set(state => ({
            chatHistory: [
                ...state.chatHistory,
                {
                    role: 'assistant',
                    content: `✅ **Workflow '${pendingWorkflow.name}' created and activated!**

🚀 **Starting simulation...**

Watch the **Live Monitor** panel below for real-time sensor data and alerts!`,
                    time: now,
                },
            ],
            pendingWorkflow: null,
            awaitingApproval: false,
            isThinking: false,
        }));
    },

    rejectWorkflow: () => {
        const { pendingWorkflow } = get();

        if (!pendingWorkflow) return;

        const now = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

        set(state => ({
            chatHistory: [
                ...state.chatHistory,
                {
                    role: 'assistant',
                    content: `❌ **Workflow cancelled.**

I won't activate ${pendingWorkflow.name || 'the workflow'}. Let me know if you'd like to create a different workflow.`,
                    time: now,
                },
            ],
            pendingWorkflow: null,
            awaitingApproval: false,
        }));
    },

    setPendingWorkflow: (workflow) => {
        set({
            pendingWorkflow: workflow,
            awaitingApproval: workflow !== null,
        });
    },
}));

export default useAgentStore;
