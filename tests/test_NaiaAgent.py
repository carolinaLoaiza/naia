# tests/test_NaiaAgent.py
import pytest
from unittest.mock import patch
from agents.NaiaAgent import classify_intent


def test_classify_intent_with_groqchat_symptom():
    state = {"input": "I have pain in my leg"}
    intent = classify_intent(state)
    assert intent == "symptom_agent"

def test_classify_intent_with_groqchat_reminder_medication():
    state = {"input": "do I have any medication reminders?"}
    intent = classify_intent(state)
    assert intent == "reminder_medication_agent"

def test_classify_intent_with_groqchat_reminder_recovery():
    state = {"input": "do I have any recovery tasks today?"}
    intent = classify_intent(state)
    assert intent == "reminder_recovery_agent"

def test_classify_intent_with_groqchat_medical_record():
    state = {"input": "What are my allergies?"}
    intent = classify_intent(state)
    assert intent == "medical_record_agent"

def test_classify_intent_with_groqchat_recommendation():
    state = {"input": "What should I do if I have pain in my leg?"}
    intent = classify_intent(state)
    assert intent == "recommendation_agent"

def test_classify_intent_with_groqchat_default():
    state = {"input": "How is the weather today?"}
    intent = classify_intent(state)
    assert intent == "chat_agent"