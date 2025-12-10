# app/states/agent_state.py
"""Reflex state for the Nexus AI Agent chat interface with streaming support."""
import reflex as rx
from typing import List, Optional, Dict, Any
import datetime
import asyncio
import os


class AgentState(rx.State):
    """State for the AI Agent chat interface with streaming."""
    
    # Chat state
    chat_history: List[dict] = []
    chat_input: str = ""
    is_thinking: bool = False
    error_message: str = ""
    
    # Streaming state
    streaming_response: str = ""
    is_streaming: bool = False
    
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
        """Send a message to the AI agent with streaming response."""
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
        self.is_streaming = True
        self.streaming_response = ""
        self.error_message = ""
        
        # Add empty assistant message for streaming
        now = datetime.datetime.now().strftime("%H:%M")
        self.chat_history = [
            *self.chat_history,
            {"role": "assistant", "content": "", "time": now}
        ]
        yield
        
        try:
            # Check for API key first
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                self.chat_history[-1]["content"] = "⚠️ **OpenAI API Key not configured**\n\nPlease add `OPENAI_API_KEY=sk-...` to your `.env` file and restart the app."
                self.is_thinking = False
                self.is_streaming = False
                return
            
            # Detect if this is an action request that needs tools
            action_keywords = [
                'create', 'workflow', 'alert', 'notify', 'send', 'email', 'whatsapp', 'monitor', 'watch',
                'yes', 'proceed', 'confirm', 'approve', 'okay', 'ok', 'sure', 'do it', 'go ahead', 'correct', 'right'
            ]
            message_lower = message.lower()
            needs_tools = any(kw in message_lower for kw in action_keywords)
            
            if needs_tools:
                # Use full agent with tools for action requests
                response = await self._process_message(message)
                self.chat_history[-1]["content"] = response["response"]
                
                # Check for pending workflow
                if response.get("awaiting_approval"):
                    self.pending_workflow = response.get("pending_workflow")
                    self.awaiting_approval = True
            else:
                # Use streaming for general questions
                try:
                    async for chunk in self._stream_response(message):
                        self.streaming_response += chunk
                        self.chat_history[-1]["content"] = self.streaming_response
                        yield  # Update UI with each chunk
                except Exception as stream_error:
                    print(f"Streaming failed, falling back to agent: {stream_error}")
                    response = await self._process_message(message)
                    self.chat_history[-1]["content"] = response["response"]
                    
                    if response.get("awaiting_approval"):
                        self.pending_workflow = response.get("pending_workflow")
                        self.awaiting_approval = True
            
        except Exception as e:
            self.error_message = str(e)
            self.chat_history[-1]["content"] = f"⚠️ I encountered an error: {str(e)}\n\nPlease check that the OPENAI_API_KEY is set in your .env file."
        
        finally:
            self.is_thinking = False
            self.is_streaming = False
            self.streaming_response = ""
    
    async def _stream_response(self, message: str):
        """Stream response from LLM token by token using langchain streaming."""
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        from app.agents.prompts import SYSTEM_PROMPT
        
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        llm = ChatOpenAI(
            model=model,
            temperature=0.3,
            api_key=api_key,
            streaming=True
        )
        
        # Build messages from history
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        
        for msg in self.chat_history[-10:]:  # Last 10 messages
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant" and msg["content"]:
                messages.append(AIMessage(content=msg["content"]))
        
        # Add current message
        messages.append(HumanMessage(content=message))
        
        # Stream response
        async for chunk in llm.astream(messages):
            if chunk.content:
                yield chunk.content
    
    async def _process_message(self, message: str) -> Dict[str, Any]:
        """Process message through the LangGraph agent (non-streaming fallback)."""
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
        """Approve workflow, save to DB, and start simulation."""
        if not self.pending_workflow:
            return

        self.is_thinking = True
        yield

        try:
            from app.services.workflow_service import workflow_service
            from app.states.simulation_state import SimulationState

            # Create workflow using shared service
            result = workflow_service.create_workflow_from_spec(self.pending_workflow)

            # Save to database
            success = workflow_service.save_workflow(
                result["workflow_id"],
                result["name"],
                result["nodes"],
                result["edges"],
                status="active"
            )

            if success:
                workflow_name = self.pending_workflow.get("name", "New Workflow")

                self._add_message(
                    f"✅ **Workflow '{workflow_name}' created and activated!**\n\n"
                    f"🚀 **Starting simulation...**\n\n"
                    f"Watch the **Live Monitor** panel below for real-time sensor data and alerts!",
                    "assistant"
                )

                self.pending_workflow = None
                self.awaiting_approval = False

                yield

                # Direct state-to-state call (like the UI does)
                # Get the SimulationState instance and call start_simulation
                sim_state = await self.get_state(SimulationState)
                sim_state.start_simulation(
                    nodes=result["nodes"],
                    edges=result["edges"]
                )

                print(f"[AgentState] ✓ Simulation started with {len(result['nodes'])} nodes, {len(result['edges'])} edges")
            else:
                self._add_message(
                    "⚠️ Failed to save workflow to database. Please try again.",
                    "assistant"
                )

            self.pending_workflow = None
            self.awaiting_approval = False

        except Exception as e:
            self._add_message(f"⚠️ Error activating workflow: {str(e)}", "assistant")
            print(f"[AgentState] Error: {e}")

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
        self.streaming_response = ""
        self.is_streaming = False
    
    def _add_message(self, content: str, role: str):
        """Add a message to chat history."""
        now = datetime.datetime.now().strftime("%H:%M")
        self.chat_history = [
            *self.chat_history,
            {"role": role, "content": content, "time": now}
        ]
