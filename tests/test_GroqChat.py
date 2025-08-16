import pytest
from unittest.mock import patch
from app.GroqChat import GroqChat


@pytest.fixture
def groq():
    """Fixture que crea instancia de GroqChat y permite mockear classifier_llm"""
    g = GroqChat()
    return g

def test_extract_symptoms_valid_json(groq):
    user_input = "I have pain in my knee for 3 days, something moderate."
    result = groq.extract_symptoms(user_input)
    assert result["overall_severity"] == "moderate"
    assert result["symptoms"][0]["name"] == "pain"
    assert result["symptoms"][0]["location"] == "knee"

def test_extract_symptoms_with_bad_chars(groq):
    result = groq.extract_symptoms("I do not have any severe symptoms.")
    assert result["overall_severity"] == "unknown"
    assert result["symptoms"] == []


def test_extract_duration_valid_number(groq):
    result = groq.extract_duration_from_text("I have pain for 5 days", "pain")    
    assert result == 5

def test_extract_duration_negative_number_clamped_to_zero(groq):
    result = groq.extract_duration_from_text("I've been in pain for days.", "pain")
    assert result == 1  


def test_classify_severity_returns_mild(groq):
    patient_context = {
        "surgery": "appendectomy",
        "medications": [{"name": "ibuprofen"}],
        "pre_existing_conditions": [{"name": "hypertension"}]
    }
    result = groq.classify_severity("eye dryness", patient_context, 2)
    assert result == "mild"    

def test_classify_severity_returns_moderate(groq):
    patient_context = {
        "surgery": "appendectomy",
        "medications": [{"name": "ibuprofen"}],
        "pre_existing_conditions": [{"name": "hypertension"}]
    }
    result = groq.classify_severity("abdominal pain", patient_context, 2)
    assert result == "moderate"   

def test_classify_severity_returns_severe(groq):
    patient_context = {"surgery": "hip replacement", "medications": [], "pre_existing_conditions": []}
    result = groq.classify_severity("blood wound", patient_context, 7)
    assert result == "severe"

def test_extract_taken_medication_valid_name(groq):
    result = groq.extract_taken_medication("I took my paracethamol")
    assert result == "paracetamol"  # se espera lower()


def test_extract_taken_medication_returns_none(groq):
    result = groq.extract_taken_medication("I feel better ")
    assert result == "none"

def test_search_for_tasks_to_mark_valid_match(groq):
    tasks_str = "1. Walk 10 minutes\n2. Do breathing exercises\n3. Apply ice pack"
    user_input = "I just did my breathing exercises"
    result = groq.search_for_tasks_to_mark(tasks_str, user_input)
    assert result == "2"

def test_search_for_tasks_to_mark_no_match(groq):
    tasks_str = "1. Apply ice pack\n2. Do breathing exercises"
    user_input = "I just had a coffee"
    result = groq.search_for_tasks_to_mark(tasks_str, user_input)
    assert result == "none"

def test_search_for_tasks_to_mark_extra_spaces(groq):
    tasks_str = "1. Walk 10 minutes\n2. Breathing exercises\n3. Stretching"
    user_input = "I just stretched"
    result = groq.search_for_tasks_to_mark(tasks_str, user_input)
    assert result == "3"  

def test_get_reminder_information_found_doctor(groq):
    reminders = [
        {"activity": "Drink water", "type": "personal", "time": "08:00", "details": "2 glasses"},
        {"activity": "Take medication", "type": "doctor", "time": "09:00", "details": "Breakfast"}
    ]
    user_input = "I already took my medication"
    result = groq.get_reminder_information(user_input, reminders)
    assert result == "YES|DOCTOR"

def test_get_reminder_information_found_personal(groq):
    reminders = [
        {"activity": "Drink water", "type": "personal", "time": "08:00", "details": "2 glasses"},
        {"activity": "Take medication", "type": "doctor", "time": "09:00", "details": "Breakfast"}
    ]
    user_input = "I drunk water"
    result = groq.get_reminder_information(user_input, reminders)
    assert result == "YES|PERSONAL"

def test_get_reminder_information_found_personal(groq):
    reminders = [
        {"activity": "Drink water", "type": "personal", "time": "08:00", "details": "2 glasses"},
        {"activity": "Take medication", "type": "doctor", "time": "09:00", "details": "Breakfast"}
    ]
    user_input = "I applied ice in the knee"
    result = groq.get_reminder_information(user_input, reminders)
    assert result == "NO"

def test_extract_reminder_info_simple_full(groq):
    user_input = "Apply ice to the knee every 4 hours for 2 days at 09:00 and 15:00, notes: swelling reduction"
    result = groq.extract_reminder_info_simple(user_input)
    assert isinstance(result, str)
    assert '"activity": "Apply ice to the knee"' in result
    assert '"total_days": 2' in result
    assert '"preferred_times": ["09:00", "15:00"]' in result

def test_extract_reminder_info_simple_none(groq):
    user_input = "Just saying hi"
    result = groq.extract_reminder_info_simple(user_input)
    assert isinstance(result, str)
    assert '"activity": null' in result
    assert '"total_days": 0' in result
    assert '"preferred_times": []' in result

