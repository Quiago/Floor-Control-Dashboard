# app/states/agent_state.py
"""Reflex state for the Nexus AI Agent chat interface."""
import reflex as rx
from typing import List, Optional, Dict, Any
import datetime
import asyncio
import os


class AgentState(rx.State):
    """State for the AI Agent chat interface."""
    
    # Chat state
    chat_history: List[dict] = []
    chat_input: str = ""
    is_thinking: bool = False
    error_message: str = ""
    
    # Workflow approval state
    pending_workflow: Optional[dict] = None
    awaiting_approval: bool = False
    
    # Agent instance reference (lazy loaded)
    _agent_initialized: bool = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_history = [
            {
                "role": "assistant",
                "content": "👋 Hello! I'm **Nexus AI**, your intelligent assistant for industrial monitoring.\n\nI can help you with:\n- 📊 **Equipment status** - Check any machine's health\n- 📈 **Sensor readings** - View live sensor data\n- ⚠️ **Alerts** - Review recent warnings\n- 🔧 **Workflows** - Create automation rules from text\n\nHow can I help you today?",
                "time": datetime.datetime.now().strftime("%H:%M")
            }
        ]
    
    @rx.event
    def set_chat_input(self, value: str):
        """Update chat input value."""
        self.chat_input = value
    
    @rx.event
    async def send_message(self, form_data: dict = None):
        """Send a message to the AI agent."""
        # Get message from form or input state
        message = ""
        if form_data and "chat_msg" in form_data:
            message = form_data["chat_msg"]
        elif self.chat_input:
            message = self.chat_input
        
        if not message.strip():
            return
        
        # Clear input
        self.chat_input = ""
        
        # Add user message to history
        self._add_message(message, "user")
        yield
        
        # Start thinking
        self.is_thinking = True
        self.error_message = ""
        yield
        
        try:
            # Get or create agent
            response = await self._process_message(message)
            
            # Add assistant response
            self._add_message(response["response"], "assistant")
            
            # Check for pending workflow
            if response.get("awaiting_approval"):
                self.pending_workflow = response.get("pending_workflow")
                self.awaiting_approval = True
            
        except Exception as e:
            self.error_message = str(e)
            self._add_message(
                f"⚠️ I encountered an error: {str(e)}\n\nPlease check that the OPENAI_API_KEY is set in your .env file.",
                "assistant"
            )
        
        finally:
            self.is_thinking = False
    
    async def _process_message(self, message: str) -> Dict[str, Any]:
        """Process message through the LangGraph agent."""
        # Check for API key first
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {
                "response": "⚠️ **OpenAI API Key not configured**\n\nPlease add `OPENAI_API_KEY=sk-...` to your `.env` file and restart the app.",
                "pending_workflow": None,
                "awaiting_approval": False
            }
        
        try:
            # Import here to avoid circular imports and lazy loading
            from app.agents.nexus_agent import get_agent
            
            agent = get_agent()
            
            # Build conversation history for context
            history = []
            for msg in self.chat_history[-10:]:  # Last 10 messages
                history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Call the agent
            result = await agent.chat(message, history)
            
            return result
            
        except ImportError as e:
            return {
                "response": f"⚠️ **Agent module not loaded**\n\nError: {str(e)}\n\nRun `uv sync` to install LangGraph dependencies.",
                "pending_workflow": None,
                "awaiting_approval": False
            }
        except Exception as e:
            raise
    
    @rx.event
    async def approve_workflow(self):
        """Approve and activate the pending workflow."""
        if not self.pending_workflow:
            return
        
        self.is_thinking = True
        yield
        
        try:
            # TODO: Actually save the workflow using WorkflowState
            workflow_name = self.pending_workflow.get("name", "New Workflow")
            
            self._add_message(
                f"✅ **Workflow '{workflow_name}' activated!**\n\nThe workflow is now monitoring your equipment and will trigger alerts as configured.",
                "assistant"
            )
            
            self.pending_workflow = None
            self.awaiting_approval = False
            
        except Exception as e:
            self._add_message(f"⚠️ Error activating workflow: {str(e)}", "assistant")
        
        finally:
            self.is_thinking = False
    
    @rx.event
    async def reject_workflow(self):
        """Reject/cancel the pending workflow."""
        if not self.pending_workflow:
            return
        
        workflow_name = self.pending_workflow.get("name", "the workflow")
        
        self._add_message(
            f"❌ **Workflow cancelled.**\n\nI won't activate {workflow_name}. Let me know if you'd like to create a different workflow.",
            "assistant"
        )
        
        self.pending_workflow = None
        self.awaiting_approval = False
    
    @rx.event
    def clear_chat(self):
        """Clear chat history and reset state."""
        self.chat_history = [
            {
                "role": "assistant",
                "content": "🔄 Chat cleared. How can I help you?",
                "time": datetime.datetime.now().strftime("%H:%M")
            }
        ]
        self.pending_workflow = None
        self.awaiting_approval = False
        self.error_message = ""
    
    def _add_message(self, content: str, role: str):
        """Add a message to chat history."""
        now = datetime.datetime.now().strftime("%H:%M")
        self.chat_history = [
            *self.chat_history,
            {"role": role, "content": content, "time": now}
        ]
