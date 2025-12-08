# app/agents/nexus_agent.py
"""LangGraph-based Nexus AI Agent for industrial equipment monitoring."""
import os
from typing import TypedDict, Annotated, Sequence, Optional, List, Dict, Any
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from .prompts import SYSTEM_PROMPT
from .tools import ALL_TOOLS


class AgentGraphState(TypedDict):
    """State for the LangGraph agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    pending_workflow: Optional[Dict[str, Any]]
    awaiting_approval: bool


class NexusAgent:
    """LangGraph-based AI agent for Nexus industrial monitoring."""
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        max_context_messages: int = 20
    ):
        """Initialize the Nexus Agent.
        
        Args:
            model: OpenAI model to use
            temperature: Creativity setting (0-1)
            max_context_messages: Maximum messages to keep in context
        """
        self.model_name = model
        self.temperature = temperature
        self.max_context_messages = max_context_messages
        
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key
        )
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(ALL_TOOLS)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Define the nodes
        def call_model(state: AgentGraphState) -> AgentGraphState:
            """Call the LLM with current context."""
            messages = list(state["messages"])
            
            # Add system prompt if not present
            if not messages or not isinstance(messages[0], SystemMessage):
                messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
            
            # Trim context if too long
            if len(messages) > self.max_context_messages:
                # Keep system prompt + last N messages
                messages = [messages[0]] + messages[-(self.max_context_messages - 1):]
            
            # Call LLM
            response = self.llm_with_tools.invoke(messages)
            
            return {"messages": [response], "pending_workflow": state.get("pending_workflow"), "awaiting_approval": state.get("awaiting_approval", False)}
        
        def should_continue(state: AgentGraphState) -> str:
            """Determine if we should continue to tools or end."""
            messages = state["messages"]
            last_message = messages[-1]
            
            # If LLM made tool calls, route to tools
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            
            # Otherwise, we're done
            return "end"
        
        # Build the graph
        workflow = StateGraph(AgentGraphState)
        
        # Add nodes
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(ALL_TOOLS))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                "end": END,
            }
        )
        
        # After tools, go back to agent
        workflow.add_edge("tools", "agent")
        
        # Compile
        return workflow.compile()
    
    async def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Process a chat message and return the response.
        
        Args:
            message: User's message
            conversation_history: Previous messages in format [{"role": "user/assistant", "content": "..."}]
        
        Returns:
            Dict with response text and any pending actions
        """
        # Build messages from history
        messages = []
        
        if conversation_history:
            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        # Add current message
        messages.append(HumanMessage(content=message))
        
        # Initial state
        initial_state: AgentGraphState = {
            "messages": messages,
            "pending_workflow": None,
            "awaiting_approval": False
        }
        
        # Run the graph
        result = await self.graph.ainvoke(initial_state)
        
        # Extract response
        final_messages = result["messages"]
        response_text = ""
        pending_workflow = None
        
        for msg in reversed(final_messages):
            if isinstance(msg, AIMessage) and msg.content:
                response_text = msg.content
                break
        
        # Check for workflow creation (parse from tool results if present)
        for msg in final_messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for call in msg.tool_calls:
                    if call.get("name") == "create_workflow":
                        # There's a pending workflow
                        pending_workflow = call.get("args", {})
        
        return {
            "response": response_text,
            "pending_workflow": pending_workflow,
            "awaiting_approval": pending_workflow is not None
        }
    
    def chat_sync(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Synchronous version of chat for non-async contexts."""
        import asyncio
        return asyncio.run(self.chat(message, conversation_history))


# Factory function for easy creation
def create_agent(
    model: str = None,
    temperature: float = 0.3
) -> NexusAgent:
    """Create a NexusAgent instance.
    
    Args:
        model: OpenAI model (defaults to OPENAI_MODEL env var or gpt-4o-mini)
        temperature: Creativity setting
    
    Returns:
        Configured NexusAgent
    """
    if model is None:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    return NexusAgent(model=model, temperature=temperature)


# Singleton instance (lazy loaded)
_agent_instance: Optional[NexusAgent] = None


def get_agent() -> NexusAgent:
    """Get or create the singleton agent instance."""
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = create_agent()
    
    return _agent_instance
