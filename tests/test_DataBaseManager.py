# tests/test_db_manager_integration.py
import streamlit as st
from data.DataBaseManager import DatabaseManager
from pymongo.collection import Collection

def test_get_collection_returns_mongo_collection(monkeypatch):
    db_manager = DatabaseManager()
    collection = db_manager.get_collection("chat_history")
    assert isinstance(collection, Collection)
    doc_count = collection.count_documents({})
    assert isinstance(doc_count, int)
