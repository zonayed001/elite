# ELITE-2026-AI — Project Documentation

## What This Project Is

**ELITE** is an online learning management system (LMS) built with Flask. It connects students with instructors in a full-featured education platform where users can browse courses, enroll in content, and learn at their own pace.

### Core Capabilities

- **User Roles** — Students can browse and enroll; instructors can apply to teach and manage courses; admins oversee the entire platform
- **Course Catalog** — Courses organized by category with ratings, pricing, and rich content (PDFs, playlists, weekly modules)
- **Instructor Applications** — Aspiring instructors submit applications reviewed by admins
- **Enrollment & Progress Tracking** — Students enroll in courses and track their progress by category
- **Support System** — Built-in support ticket system for student requests
- **Admin Dashboard** — Complete platform management interface

---

## Installation Guide

### Requirements

- Python 3 with pip
- No external database server required (SQLite by default)

### Step-by-Step Setup

**1. Navigate to the project directory**

```bash
cd ELITE-2026-AI
```

**2. Create and activate a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install all dependencies**

```bash
pip install -r requirements.txt
```

Dependencies include:
- `Flask` + `Flask-SocketIO` + `Flask-SQLAlchemy` — web framework
- `SQLAlchemy` — ORM with SQLite support
- `pymongo` — MongoDB support
- `python-dotenv` — environment variable management
- `Werkzeug`, `requests`, `BeautifulSoup4` — utilities

**4. Configure environment variables**

Create or edit a `.env` file in the project root:

```bash
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
NVIDIA_API_KEY=your_nvidia_api_key_here
```

> **Note:** The `.env` file already exists and contains an `OPENROUTER_API_KEY` placeholder. Replace it with your own key from [openrouter.ai](https://openrouter.ai).

**5. (Optional) Seed dummy data**

```bash
python add_dummy_data.py
```

This populates the database with sample courses, categories, and users for testing.

**6. Run the application**

```bash
python app.py
```

The app will start on `http://localhost:5000` (or the port specified in your environment).

---

## The AI Feature: Elite AI Chatbot

The standout feature of ELITE is its **AI-powered chatbot assistant** — "Elite AI" — which provides contextual, role-aware help throughout the platform. This is not a generic chatbot; it is deeply integrated into the platform's pages, user roles, and real-time site data.

### How Elite AI Works

Elite AI is built on **OpenRouter**, an API aggregator that connects to multiple LLM providers. By default it uses the `nvidia/nemotron-3-super-120b-a12b:free` model, and can fall back to NVIDIA's API if configured.

**Request Flow:**

```
User clicks chatbot widget on any page
         ↓
Frontend sends message + current route to /api/chatbot
         ↓
Backend builds a rich system prompt containing:
    - Who Elite AI is (friendly LMS assistant)
    - What page the user is on (page-specific guidance)
    - The user's role and name (admin / instructor / student)
    - Real-time platform stats (total courses, users, etc.)
    - Last 8 messages of conversation history
         ↓
OpenRouter API returns a reasoning-enabled response
         ↓
Response rendered safely in the chatbot widget
```

### Key AI Capabilities

#### 1. Page-Aware Guidance
The chatbot knows which page the user is on and tailors its help accordingly:

| Page | Elite AI Behavior |
|------|-------------------|
| `/courses` | Guides users on browsing, filtering, enrolling |
| `/enroll/<id>` | Explains course content, downloads, playlists |
| `/profile` | Helps navigate dashboard, track progress |
| `/admin` | Assists with platform management tasks |
| Any page | General platform questions |

This is implemented by injecting `page_context` into the system prompt at `app.py:489–580`.

#### 2. Role-Aware Responses
Elite AI adapts its tone and suggestions based on the logged-in user's role:

- **Students** — Get help with enrollment, course navigation, progress tracking
- **Instructors** — Receive guidance on course management, content uploads
- **Admins** — Get platform administration assistance

User context (role + name) is attached to every API call so the AI can personalize responses.

#### 3. Real-Time Platform Context
Every chatbot request includes live data pulled from the database:

- Total number of courses, instructors, and users
- List of categories and latest courses
- Active enrollments and support requests

This means Elite AI can answer questions like *"What courses are new this week?"* or *"How many students are enrolled in my course?"* with accurate, up-to-date information.

#### 4. Conversation Memory
The chatbot maintains the last 8 messages of conversation history, sanitized and attached to each new request. This allows for natural back-and-forth dialogue rather than one-shot interactions.

#### 5. Safe HTML Rendering
AI responses are rendered as HTML in the widget. The pipeline sanitizes all output through **DOMPurify** and parses markdown via **marked.js**, preventing XSS while preserving formatting.

### Backend Architecture

```
app.py
├── /api/chatbot          POST endpoint (lines 489–580)
│   ├── Builds system prompt with:
│   │   ├── Base identity prompt ("You are Elite AI...")
│   │   ├── Page-specific guidance (per-route instructions)
│   │   ├── User context (role, name, enrollments)
│   │   ├── Site statistics (live DB queries)
│   │   └── Conversation history (last 8 messages)
│   ├── Calls OpenRouter API with reasoning enabled
│   ├── Returns JSON { response: string }
│   └── Handles errors gracefully (API failures → user-friendly message)
```

### Frontend Architecture

```
static/assets/js/site-chatbot.js   ← loads chatbot widget independently
templates/chatbot_widget.html       ← the bot avatar + message panel UI
```

The chatbot widget appears on every page, built as a standalone SVG-based bot avatar that expands into a message panel. It communicates with the `/api/chatbot` endpoint via fetch.

### Configuration Options

| Environment Variable | Default | Description |
|--------------------|---------|-------------|
| `OPENROUTER_API_KEY` | *(required)* | API key from openrouter.ai |
| `OPENROUTER_MODEL` | `nvidia/nemotron-3-super-120b-a12b:free` | Model to use |
| `NVIDIA_API_KEY` | *(optional)* | Fallback AI provider |
| `API_TIMEOUT` | 30 | Request timeout in seconds |

### Why This AI Integration Is Helpful

1. **Reduces support load** — Students get instant answers to common questions without waiting for human support
2. **Contextual from the start** — Unlike generic chatbots, Elite AI knows exactly what page the user is on and what their role is
3. **Always learning from real data** — Live platform statistics are injected into every prompt, so the AI's answers reflect the actual state of the platform
4. **Conversational persistence** — Users can ask follow-up questions because conversation history is preserved
5. **Safe by design** — Output sanitization ensures the AI's HTML responses can't introduce security vulnerabilities

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask (Python) |
| Database | SQLite via SQLAlchemy ORM |
| Real-time | Flask-SocketIO |
| AI Backend | OpenRouter API (NVIDIA model by default) |
| Frontend | Jinja2 templates + vanilla JS/CSS |
| Auth | Werkzeug (password hashing) |

---

## Project Structure

```
ELITE-2026-AI/
├── app.py                  # Main Flask application + all routes
├── add_dummy_data.py       # Database seeder for testing
├── requirements.txt        # Python dependencies
├── .env                     # Environment variables (API keys)
├── templates/               # Jinja2 HTML templates
│   └── chatbot_widget.html  # AI chatbot widget UI
├── static/assets/js/        # Frontend JavaScript
│   └── site-chatbot.js      # Chatbot frontend logic
└── database.db             # SQLite database (created on first run)
```

