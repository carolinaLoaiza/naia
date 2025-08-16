# tests/test_db_manager_integration.py
import streamlit as st
from data.DataBaseManager import DatabaseManager
from pymongo.collection import Collection

def test_get_collection_returns_mongo_collection(monkeypatch):
    # Configurar un MONGO_URI de prueba
   # monkeypatch.setattr(st, "secrets", {"MONGO_URI": "mongodb+srv://usuario:pass@cluster/test_db"})

    db_manager = DatabaseManager()
    collection = db_manager.get_collection("chat_history")

    # Verifica que devuelve una colección válida
    assert isinstance(collection, Collection)

    # Prueba una operación simple
    doc_count = collection.count_documents({})
    assert isinstance(doc_count, int)
