from langgraph.graph import MessagesState
from pydantic import Field

class GraphInnerState(MessagesState):
    """
    Contains the inner state of the graph, including messages and any other relevant information.
    """
    customer_id: str = Field(..., description="The unique identifier for the customer.")
    loaded_preferences: str = Field("", description="Customer's loaded preferences from previous interactions.")
    remaining_steps: int = Field(10, description="Maximum number of steps remaining for graph execution to prevent infinite loops in supervisor routing.")
