import streamlit as st
from pymongo import MongoClient

class DatabaseManager:
    def __init__(self):
        self.client = MongoClient(st.secrets["MONGO_URI"])
        self.db = self.client["naia_db"]

    def get_collection(self, name):
        return self.db[name]
