# app/services/pending_simulation.py
"""
Shared storage for pending simulation data.

This simple module acts as a bridge between AgentState (which creates workflows)
and SimulationState (which runs simulations). It avoids cross-state event calls
which can cause React Hooks order issues.
"""
from typing import Dict, List, Any, Optional


class PendingSimulation:
    """Shared storage for pending simulation from chatbot approval."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._nodes = None
            cls._instance._edges = None
            cls._instance._workflow_id = None
        return cls._instance
    
    def set_workflow(self, workflow_id: str, nodes: List[Dict], edges: List[Dict]):
        """Store pending workflow data for simulation to pick up."""
        self._workflow_id = workflow_id
        self._nodes = nodes
        self._edges = edges
        print(f"[PendingSimulation] Stored workflow {workflow_id} with {len(nodes)} nodes")
    
    def get_workflow(self) -> Optional[Dict]:
        """Get pending workflow data if available."""
        if self._nodes and self._edges:
            return {
                "workflow_id": self._workflow_id,
                "nodes": self._nodes,
                "edges": self._edges
            }
        return None
    
    def clear(self):
        """Clear the pending workflow."""
        self._workflow_id = None
        self._nodes = None
        self._edges = None
    
    @property
    def has_pending(self) -> bool:
        """Check if there's a pending simulation."""
        return self._nodes is not None and self._edges is not None


# Singleton instance
pending_simulation = PendingSimulation()
