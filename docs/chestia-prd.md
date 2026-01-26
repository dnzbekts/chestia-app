# Chestia Product Requirements Document (PRD)

## 1. Overview
Chestia is an intelligent, multi-agent recipe generation platform. It leverages a sophisticated backend to create accurate cooking recipes based on user-supplied ingredients. The system ensures recipe validity through hallucination checks and a human-in-the-loop approval process for any necessary modifications.

## 2. Technology Stack
- **Backend Language:** Python v3.14
- **Backend Runtime:** Node.js v25
- **Agent Orchestration:** LangGraph, CrewAI
- **Database:** SQLite
- **Frontend Integration:** CopilotKit
- **Frontend Framework:** Next.js (Existing)

## 3. Backend Specifications

### 3.1. Core Functionality
- **Scope Restriction:** The system must strictly answer **only** recipe generation requests based on ingredients. It must refuse all other non-food-related queries.
- **Input:** List of ingredients provided by the user.
- **Workflow:**
    1.  **Database Lookup:** Search the SQLite database for an existing approved recipe using the provided ingredients.
    2.  **Generation:** If no match is found, invoke LangGraph/CrewAI agents to generate a recipe.
    3.  **Strict Constraint:** Ideally use only provided ingredients.
    4.  **Fallback Strategy:** If a viable recipe cannot be formed, agents are allowed to add a maximum of **1 or 2** additional ingredients.

### 3.2. Human-in-the-Loop Approval Process
- **Condition:** Triggered when the system needs to add extra ingredients.
- **Flow:**
    1.  Ask user for approval regarding the specific extra ingredients.
    2.  **Approval:** If approved, generate and serve the final recipe.
    3.  **Rejection:** If rejected:
        - Re-evaluate and attempt to generate a *different* recipe (potentially with different or no extra ingredients).
        - Request approval again.
    - **Looping:** This cycle repeats until the user approves.
    - **Constraint:** The system must not suggest the same rejected recipe/combination twice in the same session.

### 3.3. Validation & Hallucination Control
- **Recipe Verification:** Agents must verify that the generated recipe is logically sound and chemically possible.
- **Hallucination Check:** A dedicated step/agent to cross-reference the generated recipe against known culinary logic to prevent fabricated or dangerous results.

### 3.4. Data Persistence (SQLite)
- **Recipe Storage:** All successfully generated and user-approved recipes are stored in SQLite.
- **Caching Mechanism:** Future requests with identical inputs must fetch the recipe from the database first, bypassing the LLM to save costs and time.
- **Log storage:** Store errors and application logs.

## 4. Frontend Specifications (Chestia-Web)

### 4.1. Architecture
- **CopilotKit Role:** Functions strictly as a **bridge**. It forwards user inputs to the backend and renders the responses.
- **Intelligence:** The frontend *must not* attempt to generate answers or recipes itself.

### 4.2. Error Handling & Reliability
- **Connection Issues:**
    - Implement a **Retry Mechanism** for backend requests.
    - **Limit:** Maximum of **3 retries** upon failure/timeout.
- **User Feedback:**
    - If all retries fail, display the specific message: *"Currently unable to process your transaction. Please try again."* (or equivalent).
- **Error Logging:** All frontend/bridge failures must be sent to the backend and logged in the SQLite database.

## 5. Non-Functional Requirements

### 5.1. Testing
- **Unit & Integration Tests:** Complete coverage required for all agents and API endpoints.
- **Edge Cases:**
    - Prevention of infinite loops in the user approval phase.
    - Handling of empty ingredient lists or gibberish input.
    - Graceful handling of backend timeouts.

### 5.2. Robustness
- The system logic must ensure that users are never left in a hanging state and that modifications are always consensual.
