import json
import os
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from data.DataBaseManager import DatabaseManager

class ChatHistoryManager:
    """
    Manages chat history for a user in a post-surgery recovery assistant context.

    Stores and retrieves messages from a MongoDB collection, preserving the roles
    (user, assistant, system) and enabling conversation continuity.
    
    Attributes:
        user_id (str): The patient's unique identifier.
        collection (pymongo collection): MongoDB collection for storing chat history.
    """
    def __init__(self, user_id):
        """
        Initializes the ChatHistoryManager for a given user.

        Args:
            user_id (str): Unique identifier for the patient.
        """
        self.user_id = user_id
        db_manager = DatabaseManager()
        self.collection = db_manager.get_collection("chat_history")

    def load(self):
        """
        Loads the chat history for the user from the database.

        Returns:
            list[BaseMessage]: A list of HumanMessage, AIMessage, or SystemMessage
            objects representing the chat history. If no history exists, returns a
            default system message for the recovery assistant.
        """
        doc = self.collection.find_one({"patient_id": self.user_id})
        if doc and "history" in doc:
            return [
                HumanMessage(m["content"]) if m["role"] == "user"
                else AIMessage(m["content"]) if m["role"] == "assistant"
                else SystemMessage(m["content"])
                for m in doc["history"]
            ]
        else:
            # Default system message for new users or empty history
            return [SystemMessage(content="You are a helpful assistant for post-surgery recovery.")]
   
    def save(self, messages):
        """
        Saves the provided chat messages to the database.

        Converts the message objects into a serializable format with roles.

        Args:
            messages (list[BaseMessage]): List of messages (HumanMessage, AIMessage, SystemMessage) to save.
        """
        serializable = []
        for m in messages:
            role = (
                "user" if isinstance(m, HumanMessage)
                else "assistant" if isinstance(m, AIMessage)
                else "system"
            )
            serializable.append({"role": role, "content": m.content})
        # Upsert: create new document if none exists, else update existing
        self.collection.update_one(
            {"patient_id": self.user_id},
            {"$set": {"history": serializable}},
            upsert=True
        )