NAIA (Nursing AI Assistant)
Overview
NAIA is a conversational AI-powered assistant designed to support post-operative patients with their recovery journey. It combines text and voice interaction, smart symptom monitoring, medication and appointment reminders, and access to medical history to offer a personalized at-home experience.

Key Features
Symptom Tracking & Alerting
Recognizes daily symptoms and flags potential complications early.

Medication & Appointment Reminders
Sends timely reminders to ensure adherence to prescribed regimens and upcoming consultations.

Medical History Integration
Retrieves and integrates data from a simulated NHS database (via JSON) for context-aware recommendations.

Conversational AI Interface
Supports natural language queries via text and voice to offer guidance, educational content, and emotional reassurance.

Architecture & Tools
Category	Tools
AI & Agent Frameworks	LangChain, LangGraph, Whisper (OpenAI), ChatGroq
Automation & Integration	Microsoft Power Automate
Prototyping & Deployment	Flowise, Streamlit, Streamlit Cloud
Data & Infrastructure	Python, JSON
Dev Environment & Control	Visual Studio Code, Git, GitHub
Communication & Alerts	Twilio (for SMS notifications)

Getting Started
Clone the repository

bash
Copiar
Editar
git clone https://github.com/carolinaLoaiza/naia.git
cd naia
Install dependencies

bash
Copiar
Editar
pip install -r requirements.txt
Run the app

bash
Copiar
Editar
streamlit run Login.py
(Ensure JSON database files and agents folder are accessible in directory)

Contributions
Developed core modules: symptom classification, reminder scheduling, AI interaction.

Set up agile processes: sprints, backlog, user story templates, and shared workspace.

Managed deployments via GitHub and Streamlit Cloud.

Created flowcharts and system architecture diagrams to ease team collaboration.

Future Enhancements
Integrate a real-world backend with live NHS data.

Expand agent capabilities for personalized decision support.

Add user authentication and secure data storage.

Introduce analytics dashboards for patient progress tracking.
