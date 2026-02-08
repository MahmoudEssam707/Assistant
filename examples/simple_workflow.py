from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# Simple uppercase function
def uppercase_text(state):
    return {"message": state["message"].upper()}

# Create workflow
class Simple(TypedDict):
    message: str

workflow = StateGraph(Simple)

# Add nodes
workflow.add_node("uppercase", uppercase_text)

# Add edges: START -> uppercase -> END
workflow.add_edge(START, "uppercase")
workflow.add_edge("uppercase", END)

# Compile the graph
app = workflow.compile()

# # Test it
# if __name__ == "__main__":
#     result = app.invoke({"message": "Hello World"})
#     print(f"Result: {result['message']}")