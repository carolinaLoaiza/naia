import json
import os
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from data.DataBaseManager import DatabaseManager

class ChatHistoryManager:
    # def __init__(self, user_id, base_path="data/"):
    #     self.filepath = os.path.join(base_path, f"chat_history_{user_id}.json")
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
        
    # def load(self):
    #     if os.path.exists(self.filepath):
    #         try:
    #             with open(self.filepath, "r", encoding="utf-8") as f:
    #                 raw = json.load(f)
    #                 return [
    #                     HumanMessage(m["content"]) if m["role"] == "user"
    #                     else AIMessage(m["content"]) if m["role"] == "assistant"
    #                     else SystemMessage(m["content"])
    #                     for m in raw
    #                 ]
    #         except (json.JSONDecodeError, IOError):
    #             return [SystemMessage(content="You are a helpful assistant for post-surgery recovery.")]
    #     else:
    #         return [SystemMessage(content="You are a helpful assistant for post-surgery recovery.")]
   
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

    # def save(self, messages):
    #     os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
    #     serializable = []
    #     for m in messages:
    #         role = (
    #             "user" if isinstance(m, HumanMessage)
    #             else "assistant" if isinstance(m, AIMessage)
    #             else "system"
    #         )
    #         serializable.append({"role": role, "content": m.content})

    #     with open(self.filepath, "w", encoding="utf-8") as f:
    #         json.dump(serializable, f, ensure_ascii=False, indent=2)

    # def add_message(self, message):
    #     history = self.load()
    #     history.append(message)
    #     self.save(history)
        
    # def add_message(self, message):
    #     """Agrega un mensaje nuevo al historial y guarda."""
    #     history = self.load()
    #     history.append(message)
    #     self.save(history)            