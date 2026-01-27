# 🍳 Chestia

**Chestia** is an intelligent, premium culinary platform designed to generate high-quality recipes from user-provided ingredients. It uses a sophisticated multi-agent system to ensure accuracy, safety, and a "wow" user experience.

---

## ✨ Features

- **AI-Powered Recipe Generation**: Leverages Google Gemini and CrewAI to craft recipes based on what you have in your fridge.
- **Difficulty-Based Recipes**: Choose your preferred difficulty level (Easy, Intermediate, Hard) to get recipes that match your cooking skills and time availability.
- **Smart Default Ingredients**: Automatically assumes basic household staples (water, oil, salt, sugar, spices) are available, reducing user input friction and improving cache efficiency.
- **Human-in-the-Loop**: Intelligent fallback system that suggests 1-2 extra ingredients when necessary, requiring user approval.
- **Hallucination Control**: Dedicated verification agents ensure recipes are logically sound and chemically possible.
- **Smart Caching**: Approved recipes are stored in SQLite with difficulty + ingredients as cache key to provide instant results for repeated requests and save LLM costs.
- **Premium Design**: A high-end, dark-mode focused experience built with Next.js and Tailwind CSS v4.

---

## 🏗️ Architecture

Chestia follows a multi-agent orchestration pattern using **LangGraph** and **CrewAI**.

```mermaid
graph TD
    User([User Input]) --> Gateway[API Gateway /fastapi]
    Gateway --> Cache{SQLite Cache}
    Cache -- Hit --> Result([Approved Recipe])
    Cache -- Miss --> Agents[Multi-Agent System]
    
    subgraph Agents [LangGraph / CrewAI Orchestration]
        RA[Recipe Agent] --> VA[Verification Agent]
        VA --> HA[Hallucination Agent]
    end
    
    Agents -- Needs Approval --> HitL([Human-in-the-Loop])
    HitL -- Approved --> Result
    Result --> Cache
```

---

## 🛠️ Tech Stack

### Backend
- **Language**: Python v3.14
- **Orchestration**: LangGraph, CrewAI
- **LLM**: Google Gemini (via `langchain-google-genai`)
- **API**: FastAPI, Uvicorn
- **Database**: SQLite

### Frontend
- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS v4, Lucide React
- **Passive Bridge**: CopilotKit (Planned Integration)
- **State Management**: React Hooks & Zod for validation

---

## 📂 Project Structure

```text
.
├── chestia-backend/         # Python Multi-Agent Backend
│   ├── src/                 # Source code (agents, api, graph)
│   ├── tests/               # Pytest suite
│   └── requirements.txt     # Dependencies
├── chestia-web/             # Next.js Frontend
│   ├── app/                 # Next.js App Router
│   ├── components/          # Reusable UI components
│   └── package.json         # Dependencies & Scripts
├── docs/                    # Technical documentation & PRD
└── GEMINI.md                # Project Rules & Standards
```

---

## 🚀 Getting Started

### Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd chestia-backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure environment variables:
    Create a `.env` file and add your `GOOGLE_API_KEY`:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key_here
    ```
5.  Run the development server:
    ```bash
    uvicorn src.api:app --reload
    ```

### Frontend Setup

1.  Navigate to the web directory:
    ```bash
    cd chestia-web
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```

---

## 🤖 CopilotKit Process (Planned)

CopilotKit will be integrated as a **passive bridge** between the frontend and the agentic backend.

1.  **Strict Relay**: The frontend will forward user ingredient inputs via CopilotKit.
2.  **State Synchronization**: CopilotKit will manage the conversation state and specific "Human-in-the-Loop" interactions (approving/rejecting extra ingredients).
3.  **No Local Generation**: All intelligence resides in the backend; the frontend focuses strictly on presentation and relaying responses.

---

## 📜 Development Guidelines

- **TDD (Test-Driven Development)**: Write failing tests before any implementation.
- **Safety First**: All recipes must pass the hallucination check before being stored.
- **Rules**: Refer to [GEMINI.md](file:///Users/denizb/Repos/Chestia/GEMINI.md) for architectural and coding standards.

---

*Chestia - Elevating your culinary journey with AI.*
