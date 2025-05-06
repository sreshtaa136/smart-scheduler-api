# Smart Appointment Scheduler

An LLM-driven smart scheduling API built with FastAPI, MongoDB, and Google Calendar — complete with context-aware recommendations, conflict detection, availability generation, transactional booking, and email invites.

---

## 🚀 Highlights

- **Context-Aware Recommendations**  
  Uses OpenAI (gpt-4o-mini) to suggest up to 3 optimal slots based on patient preferences and provider availability.

- **Automatic Conflict Detection & Resolution**  
  Filters out any slot that overlaps an existing booking, both in the database and on Google Calendar.

- **Monthly Availability Generation**  
  Programmatically seeds half-hour windows (09:00–12:00, 13:00–17:00) on every weekday in AEST.

- **.ics Email Invitations**  
  On booking, sends the patient an email with a fully-compliant `.ics` calendar invite via SMTP—without delaying the HTTP response.

- **Modern Python Stack**  
  Async FastAPI, Pydantic v2 (`model_dump`), Motor, python-dateutil, icalendar, OpenAI-Python v1 (thread-pool wrapper), BackgroundTasks.

- **Modern user focused UI**  
  🚧 Building in progress   

---

## 🏗 Tech Stack

- **Python 3.10+**  
- **FastAPI** + **Uvicorn** (ASGI server)  
- **Motor** (async MongoDB driver)  
- **Pydantic v2** (data validation & serialization)  
- **python-dotenv** (env var management)  
- **python-dateutil** (robust ISO parsing)  
- **google-api-python-client** (Calendar read/write)  
- **OpenAI-Python v1** (LLM recommendations)  
- **icalendar** (ICS invite generation)  
- **smtplib** (SMTP email delivery)

---

## 📡 API Endpoints & Functionality

| Endpoint                                         | Method | Description                                                                                                                                                       |
|--------------------------------------------------|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Get Availability**                             | `GET`  | `/availability/{provider_id}`<br>Returns all free (unbooked) 30-minute slots for the given provider between the `start` and `end` ISO timestamps.                  |
| **Recommend Slots**                              | `POST` | `/recommend/`<br>Given a provider, time window, and patient info (`name`, `preferences`, `conditions`), returns up to 3 JSON‐formatted slot suggestions with reasons. |
| **Book Appointment**                             | `POST` | `/book/`<br>Creates a confirmed appointment:<br>1. Persists it in MongoDB<br>2. Adds it to Google Calendar<br>3. Deletes the matching availability slot (DB & Google)<br>4. Sends an `.ics` invite email to the patient |

---

## 🔧 Getting Started
1. Clone & Virtual Environment
```bash
git clone https://github.com/sreshtaa136/smart-scheduler.git
cd smart-scheduler
python3 -m venv .venv
source .venv/bin/activate
```
2. Install Dependencies
```bash
pip install -r requirements.txt
```
3. Configure Environment
Create a .env file with:
```dotenv
# MongoDB
MONGO_URI=mongodb:.../scheduler_db

# OpenAI
OPENAI_API_KEY=sk-...

# Google Calendar service account
GOOGLE_APPLICATION_CREDENTIALS=/full/path/to/service-account.json

# SMTP for email invites
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
SMTP_FROM="Clinic Scheduler <no-reply@example.com>"
```
4. Run the Server
```bash
uvicorn app.main:app --reload
```

Interactive docs: http://localhost:8000/docs

---
## 🚧 Future Enhancements
- Add JWT authentication and Role-Based Access Control.
- Email a summary of the consultation to the patient 
- Enable profile creation and provider availability management
- Persist ICS event IDs to allow rescheduling & cancellations.
- Utilise LLM in more features