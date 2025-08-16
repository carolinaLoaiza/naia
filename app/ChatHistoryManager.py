import json
import os
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from data.DataBaseManager import DatabaseManager

class ChatHistoryManager:
    def __init__(self, user_id):
        self.user_id = user_id
        db_manager = DatabaseManager()
        self.collection = db_manager.get_collection("chat_history")

    def load(self):
        doc = self.collection.find_one({"patient_id": self.user_id})
        if doc and "history" in doc:
            return [
                HumanMessage(m["content"]) if m["role"] == "user"
                else AIMessage(m["content"]) if m["role"] == "assistant"
                else SystemMessage(m["content"])
                for m in doc["history"]
            ]
        else:
            return [SystemMessage(content="You are a helpful assistant for post-surgery recovery.")]
   
    def save(self, messages):
        serializable = []
        for m in messages:
            role = (
                "user" if isinstance(m, HumanMessage)
                else "assistant" if isinstance(m, AIMessage)
                else "system"
            )
            serializable.append({"role": role, "content": m.content})

        self.collection.update_one(
            {"patient_id": self.user_id},
            {"$set": {"history": serializable}},
            upsert=True
        )