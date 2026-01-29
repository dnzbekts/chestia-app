# 🍳 Chestia

**Chestia** is an intelligent, premium culinary platform that generates high-quality recipes from user-provided ingredients. It leverages a sophisticated multi-agent AI system with Google Gemini to ensure accuracy, safety, and an exceptional user experience.

---

## ✨ Features

- **Smart Web Search**: Integrates Tavily AI to find real-world recipes before attempting LLM generation
- **AI-Powered Recipe Generation**: Leverages Google Gemini (1.5 Flash) to craft recipes based on what you have in your fridge
- **Difficulty-Based Recipes**: Choose Easy, Intermediate, or Hard to get recipes that match your cooking skills
- **Smart Default Ingredients**: Automatically assumes basic pantry staples (water, oil, salt, spices) are available
- **Auto-Retry with Suggestions**: If a recipe can't be made with your ingredients, the system automatically tries adding 1-2 extras (max 3 attempts)
- **Hallucination Control**: Verification agents ensure recipes are logically sound and don't include imaginary ingredients
- **Smart Caching**: Approved recipes are stored in SQLite. It uses dual-layer retrieval:
  - **Exact Cache Check**: Instant hit for identical ingredient lists.
  - **Semantic Search**: Fuzzy matching via vector embeddings (Gemini + `sqlite-vec`) for variations like "fusilli" vs "pasta".
- **Recipe Modification**: Don't like the result? Request a new version or add ingredients via `/modify` endpoint
- **Bilingual Support**: Full Turkish/English support for all API messages
- **Premium Design**: Dark-mode focused experience built with Next.js and Tailwind CSS v4

---

## 🏗️ Architecture

### High-Level Flow

```mermaid
graph TD
    User([User: ingredients + difficulty]) --> Filter[Filter Default Ingredients]
    Filter --> ExactCache{Exact Cache?}
    ExactCache -- Hit --> Review[Review Agent]
    ExactCache -- Miss --> SemanticCache{Semantic Search?}
    
    SemanticCache -- Hit --> Review
    SemanticCache -- Miss --> Search{"Web Search (Tavily)"}
    
    Search -- Found --> Review
    Search -- Miss --> Generate[Generate Recipe]
    
    Generate --> Review
    Review -- Yes --> Result([Return Recipe])
    Review -- No, iter<3 --> AddExtras[Add 1-2 Extras]
    AddExtras --> Generate
    Review -- No, iter>=3 --> Error([Error: No Recipe Found])
    
    Result -- User Approves --> Feedback[POST /feedback]
    Feedback --> Done([Cache & Done])
```

### Multi-Agent System

The backend orchestrates three specialized AI agents using LangGraph:

1. **RecipeAgent** (`recipe_agent.py`)
   - Generates recipes using Google Gemini 1.5 Flash (temperature: 0.7)
   - Enforces strict ingredient constraints
   - Adjusts complexity based on difficulty level

2. **SearchAgent** (`search_agent.py`)
   - Performs web searches using Tavily AI
   - Finds existing recipes to avoid unnecessary generation
   - Extracts relevant cooking information for the RecipeAgent

3. **ReviewAgent** (`review_agent.py`)
   - Validates recipes using Google Gemini 1.5 Flash (temperature: 0)
   - Checks for hallucinations and logical errors
   - Verifies difficulty appropriateness
   - Suggests additional ingredients if needed

4. **Orchestration** (`graph.py`)
   - Coordinates agent interactions via LangGraph
   - Manages auto-retry flow (max 3 iterations)
   - Handles state and error propagation

---

## 🛠️ Tech Stack

### Backend

- **Language**: Python 3.14
- **Orchestration**: LangGraph + CrewAI
- **LLM**: Google Gemini 1.5 Flash (via `langchain-google-genai`)
- **API Framework**: FastAPI + Uvicorn
- **Database**: SQLite with `sqlite-vec` extension for vector search
- **Testing**: pytest (65+ tests covering Unit, Integration, and Security)
- **Utilities & Foundation** (Clean Architecture layout):
  - `src/infrastructure/llm_factory.py`: Centralized LLM & parameter management
  - `src/infrastructure/database.py`: Context-manager based SQLite operations & `EmbeddingService`
  - `src/infrastructure/localization/i18n.py`: Bilingual message management (EN/TR)
  - `src/core/logging_config.py`: Structured application logging
  - `src/core/exceptions.py`: Domain-specific exception hierarchy

### Frontend

- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS v4 + Lucide React
- **Passive Bridge**: CopilotKit (planned integration)
- **State Management**: React Hooks & Zod for validation

---

## 📂 Project Structure

```text
.
├── chestia-backend/                     # Python Multi-Agent Backend
│   ├── src/
│   │   ├── api/                         # Presentation Layer
│   │   │   ├── routes.py                # FastAPI endpoints
│   │   │   └── schemas.py               # Pydantic request/response models
│   │   ├── core/                        # Cross-cutting Concerns
│   │   │   ├── config.py                # Application settings
│   │   │   ├── exceptions.py            # Domain-specific exceptions
│   │   │   └── logging_config.py        # Structured logging
│   │   ├── domain/                      # Business Logic
│   │   │   └── ingredients.py           # Ingredient normalization & filtering
│   │   ├── infrastructure/              # External Services
│   │   │   ├── database.py              # SQLite operations & EmbeddingService
│   │   │   ├── llm_factory.py           # Centralized LLM management
│   │   │   └── localization/            # Bilingual i18n messages
│   │   ├── workflow/                    # LangGraph Orchestration
│   │   │   ├── graph.py                 # State machine & routing
│   │   │   ├── copilotkit_adapter.py    # CopilotKit integration
│   │   │   └── agents/                  # AI Agents
│   │   │       ├── recipe_agent.py      # Recipe generation
│   │   │       ├── review_agent.py      # Validation & review
│   │   │       └── search_agent.py      # Web search
│   │   └── main.py                      # Application entry point
│   ├── tests/                           # Comprehensive Test Suite (14 files)
│   │   ├── conftest.py                  # Shared fixtures & extension loading
│   │   ├── unit_tests/                  # Layer-specific unit tests (9 files)
│   │   └── integration/                 # End-to-end & endpoint tests (4 files)
│   └── requirements.txt
├── chestia-web/                         # Next.js Frontend
│   ├── app/                             # Next.js App Router
│   ├── components/                      # Reusable UI components
│   └── package.json
├── docs/                                # Technical documentation
└── GEMINI.md                            # Project Rules & Standards
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.14+ (or 3.12+)
- Node.js 25+ (for frontend)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Backend Setup

1. **Navigate to the backend directory:**

   ```bash
   cd chestia-backend
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the `chestia-backend` directory:

   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

5. **Run the development server:**

   ```bash
   uvicorn src.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

6. **Run tests (optional):**

   ```bash
   pytest tests/ -v
   ```

### Frontend Setup

1. **Navigate to the web directory:**

   ```bash
   cd chestia-web
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Run the development server:**

   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:3000`

---

## 📡 API Endpoints

### Generate Recipe

`POST /generate`

**Request:**

```json
{
  "ingredients": ["chicken", "rice", "onion"],
  "difficulty": "easy",
  "lang": "en"  // "tr" for Turkish
}
```

**Response (Success):**

```json
{
  "status": "success",
  "recipe": {
    "name": "Simple Chicken Rice",
    "ingredients": ["chicken", "rice", "onion", "salt", "oil"],
    "steps": ["Step 1...", "Step 2..."],
    "metadata": {"cooking_time": "30 min"}
  },
  "extra_ingredients_added": [],
  "iterations": 1
}
```

**Response (Error):**

```json
{
  "status": "error",
  "message": "No suitable recipe could be found...",
  "extra_ingredients_tried": ["garlic", "tomato"]
}
```

### Modify Recipe

`POST /modify`

**Request:**

```json
{
  "original_ingredients": ["chicken", "rice", "onion"],
  "new_ingredients": ["tomato"],
  "difficulty": "intermediate",
  "modification_note": "make it spicy",
  "lang": "en"
}
```

### Submit Feedback

`POST /feedback`

**Request:**

```json
{
  "ingredients": ["chicken", "rice", "onion"],
  "difficulty": "easy",
  "approved": true,
  "recipe": { /* recipe object */ },
  "lang": "en"
}
```

---

## � Testing

The backend features a comprehensive test suite (65+ tests) following the Triple-A (Arrange-Act-Assert) pattern and TDD principles.

### Test Categories

- **Unit Tests** (`tests/unit_tests/`):
  - `test_schemas.py`: Pydantic validation and character constraints.
  - `test_ingredients.py`: Ingredient normalization and default filtering.
  - `test_exceptions.py`: Custom error hierarchy verification.
  - `test_llm_factory.py`: API key validation and LLM configuration.
  - `test_database.py`: SQLite CRUD and schema initialization.
  - `test_localization.py`: Bilingual message retrieval (EN/TR).
  - `test_recipe_agent.py`: Sanitization and LLM response parsing.
  - `test_review_agent.py`: Recipe structure and logic validation.
  - `test_graph.py`: LangGraph state machine and routing.

- **Integration Tests** (`tests/integration/`):
  - `test_endpoints.py`: End-to-end API verification for `/generate`, `/modify`, and `/feedback`.
  - `test_security.py`: Security headers (CSP, HSTS) and CORS.
  - `test_rate_limiting.py`: API resource protection verification.
  - `test_feedback_validation.py`: Schema safety for stored recipes.

### Running Tests

Run the full suite:

```bash
cd chestia-backend
source venv/bin/activate
pytest tests/ -v
```

Run specific category:

```bash
pytest tests/unit_tests/ -v
pytest tests/integration/ -v
```

---

## 🤖 CopilotKit Integration

CopilotKit serves as the **bridge** between the frontend and the agentic backend, enabling a rich AI user experience.

### Architecture

1. **Remote Endpoint**: The backend exposes a strictly typed CopilotKit endpoint at `/copilotkit`.
2. **LangGraph Adapter**: A specialized wrapper (`copilotkit_agent.py`) adapts the internal LangGraph workflow to the AG-UI protocol.
3. **State Management**: CopilotKit manages the conversation state (`messages`, `ingredients`, `recipe`) and synchronizes it between frontend and backend.
4. **Passive Execution**: The frontend does not generate recipes; it acts as a UI layer for the backend intelligence.

### Integration Points

- **Endpoint**: `POST /copilotkit` (Handled by CopilotKit SDK)
- **Agent Name**: `chestia_recipe_agent`
- **Output**: JSON-structured recipes compatible with the frontend UI components

---

## 📜 Development Guidelines

- **TDD (Test-Driven Development)**: Write failing tests before any implementation
- **Bilingual i18n**: Use `src/utils/i18n.py` for all user-facing backend messages
- **Safety First**: All recipes must pass the hallucination check before being stored
- **Strict Ingredient Control**: Filter default ingredients at the API level
- **Architecture Standards**: Refer to [GEMINI.md](GEMINI.md) for project rules and coding standards

---

## 🔒 Security & Configuration

- **CORS & Security Headers**: Strict middleware-level protection (CSP, HSTS, X-Frame-Options)
- **Rate Limiting**: Endpoint-level protection via SlowAPI (prevents AI resource abuse)
- **Input Validation**: Layered validation using Pydantic models (pinned 3-20 ingredients)
- **Enhanced Schema Safety**: Strict `RecipeSchema` validation for feedback/storage
- **RAG Context Sanitization**: Search results are summarized by LLM to mitigate indirect injection risks
- **API Key Management**: Store sensitive keys in `.env` (never commit!)
- **Error Masking**: Server errors are masked in production responses to prevent data leakage
- **Turkish Character Support**: Validation regex supports Turkish characters (ğ, ü, ş, ı, ö, ç)

---

## 📝 License

This project is private and proprietary.

---

*Chestia - Elevating your culinary journey with AI.*

---
Last reviewed: 2026-01-29 (Backend Test Suite Update)
