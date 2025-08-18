import streamlit as st
from pymongo import MongoClient

class DatabaseManager:
    """
    Manages the connection to the MongoDB database for the application.

    Attributes:
        client (MongoClient): The MongoDB client instance.
        db: The database object for 'naia_db'.
    """
    def __init__(self):
        """
        Manages the connection to the MongoDB database for the application.

        Attributes:
            client (MongoClient): The MongoDB client instance.
            db: The database object for 'naia_db'.
        """
        self.client = MongoClient(st.secrets["MONGO_URI"])
        self.db = self.client["naia_db"]

    def get_collection(self, name):
        return self.db[name]
