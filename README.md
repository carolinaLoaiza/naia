# NAIA - Nurse Artificial Intelligence Assistant

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.46.1-orange?logo=streamlit&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?logo=mongodb&logoColor=white)
![Twilio](https://img.shields.io/badge/Twilio-SMS-red?logo=twilio&logoColor=white)
![License](https://img.shields.io/badge/License-Academic-lightgrey)

NAIA (Nurse Artificial Intelligence Assistant) is designed to support post-operative patients through natural, conversational communication.  
This project is part of the MSc Artificial Intelligence Technology program at Northumbria University London, for the module *Contemporary Computing and Digital Technologies*.

---

## Features

- 24/7 real-time, chat-based interaction  
- Automated, personalized reminders for medication, wound care, mobility, and follow-up in the chat  
- SMS reminders for medication and follow-up appointments  
- Hands-free voice interaction  
- Monitors patient inputs and automatically detects red-flag symptoms  
- Runs on secure, scalable cloud services (Streamlit Cloud, MongoDB Atlas, Mock API, Twilio) and leverages public NHS data  
- Saves and reuses conversations in the Agent’s context  
- Displays all medications, tasks, appointments & symptoms at a glance  
- Recovery checklist that turns daily care into simple, achievable steps  
- Creation of custom reminders  

**Planned features (not yet implemented):**  
- Emergency calls  
- Additional support or reassurance regarding recovery progress  
- Voice tone adaptation  

---

## User Stories

- As a user, I want to log in to the application and get access to NAIA  
- As a user, I want to interact with the AI agent using both text and voice  
- As a user, I want NAIA to remember my previous conversations when I log in again  
- As a user, I want NAIA to automatically retrieve and use my medical history from the synthetic NHS database  
- As a user, I want NAIA to ask about my daily symptoms (Check-ups)  
- As a user, I want NAIA to record my current symptoms  
- As a user, I want NAIA to remind me to take my medication according to my prescription  
- As a user, I want NAIA to integrate my symptoms into my clinical history  
- As a user, I want to receive reminders about my recovery tasks  
- As a user, I want NAIA to create a daily checklist of post-operative tasks  
- As a user, I want to create my own reminders in NAIA  
- As a user, I want a FAQ section to resolve doubts about app usage  
- As a user, I want reminders for upcoming doctor’s appointments  
- As a user, I want dashboards displaying symptoms, medication schedules, recovery tasks, and follow-up appointments  

---

## Technologies

**Programming Languages:**  
- Python, JavaScript, JSON  

**Libraries:**  
- groq==0.30.0  
- langchain==0.3.26  
- langchain-groq==0.3.6  
- openai==1.97.0  
- python-dotenv==1.1.1  
- streamlit==1.46.1  
- streamlit-authenticator==0.4.2  
- streamlit-extras==0.6.0  
- streamlit-float==0.3.5  
- streamlit_chat_widget==0.2.0  
- langgraph  
- requests  
- beautifulsoup4  
- streamlit-aggrid  
- twilio  
- pymongo  
- passlib[bcrypt]==1.7.4  
- pytest  

**Database:** MongoDB  

**External APIs & Services:**  
- Mock API for synthetic data  
- Twilio for SMS notifications  
- NHS website for scraping recovery and complication information  

---

## Project Structure

```

Naia/
│
├─ Agents/
│ ├─ AgentState
│ ├─ ChatAgent
│ ├─ HealthRecommendationAgent
│ ├─ MedicalRecordAgent
│ ├─ NaiaAgent
│ ├─ ReminderAgent
│ └─ SymptomAgent
│
├─ App/
│ ├─ AppointmentManager
│ ├─ ChatHistoryManager
│ ├─ GroqChat
│ ├─ MedicalRecordManager
│ ├─ MedicationScheduleManager
│ ├─ RecoveryCheckupsScheduleManager
│ ├─ SendReminder
│ ├─ SymptomsManager
│ └─ Utilities
│
├─ Assets/
│ └─ Various images/icons
│
├─ Data/
│ └─ DataBaseManager
│
├─ Graph/
│ └─ LangGraph
│
├─ Pages/
│ ├─ Chat
│ ├─ FAQ
│ ├─ Follow-up Appointment
│ ├─ Home
│ ├─ Medications
│ ├─ Recovery Check-ups
│ └─ Symptom Tracker
│
├─ Tests/
│ ├─ Test_ChatAgent
│ ├─ Test_DatabaseManager
│ ├─ Test_GroqChat
│ └─ Test_NaiaAgent
│
└─ Login page

```
---

This README provides a clear overview of NAIA’s functionality, technology stack, user stories, and project structure, suitable for academic purposes.
