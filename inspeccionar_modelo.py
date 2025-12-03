
from app.states.workflow_state import WorkflowState
workflow = WorkflowState.toggle_category("analyzer")
print(workflow)