from typing import TypedDict

class AgentState(TypedDict):
    input: str
    output: str
    username: str
    reminder: str