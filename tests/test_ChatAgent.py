import pytest
from agents.ChatAgent import handle_chat 

def test_handle_chat_combines_reminder_and_resets():
    state = {
        "input": "Hello NAIA",
        "output": "",
        "username": "user1",
        "reminder": "Don't forget to take your meds. "
    }
    new_state = handle_chat(state)
    assert new_state["input"] == "Hello NAIA"
    assert "Don't forget to take your meds." in new_state["output"]
    assert "NAIA is here to support your health" in new_state["output"]
    assert new_state["reminder"] == ""
    assert new_state["username"] == "user1"