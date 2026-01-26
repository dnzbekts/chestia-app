# Chestia Backend Implementation Specification

Based on `chestia-prd.md`, this document details the implementation requirements for the backend services.

## 1. Technology Stack
- **Languages:** Python v3.14, Node.js v25
- **Orchestration:** LangGraph, CrewAI
- **Database:** SQLite
- **Context Protocol:** CopilotKit (Backend-side integration)

## 2. Core Architecture
- **Multi-Agent System:**
    - Agents responsible for: Recipe Database Search, Ingredient Analysis, Recipe Generation, Verification, Hallucination Check.
- **Workflow:**
    1.  **Input:** Receive ingredient list.
    2.  **Cache Check:** Query SQLite for existing recipes.
    3.  **Generation Loop:**
        -   Attempt generation with strict ingredient list.
        -   **Fallback:** If not possible, suggest 1-2 extra ingredients.
        -   **User Loop:** Require explicit user approval for extras. If rejected, retry with different options. Infinite loop prevention required.
    4.  **Verification:**
        -   Logical consistency check.
        -   **Safety/Hallucination Check:** dedicated validation step.
    5.  **Output:** Return structured recipe JSON.

## 3. Data Schema (SQLite)
- **Recipes Table:**
    - ID, Name, Ingredients (JSON), Steps (JSON), Metadata (Time, Difficulty).
- **Logs Table:**
    - Timestamp, ErrorType, Message, RequestID.

## 4. API & Integration
- **Endpoints:**
    - `/generate`: Handles main recipe request.
    - `/feedback`: Handles user approval/rejection for extra ingredients.
- **Error Handling:**
    - **Retries:** Max 3 retries for internal agent failures.
    - **Timeouts:** Graceful handling of long-running agent chains.

## 5. Testing Requirements
- **Unit Tests:** For all agent logic and helper functions.
- **Integration Tests:** For full flow from API input to SQLite persistence.
- **Edge Cases:** Empty inputs, non-food inputs, rejection loops.
