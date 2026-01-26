# GEMINI Project Rules & Guidelines

This document serves as the single source of truth for development rules, architectural standards, and project-specific constraints for the **Chestia** project.

## 1. Project Overview & Philosophy
**Chestia** is an intelligent, premium culinary platform designed to generate recipes from user-provided ingredients.
-   **Core Philosophy:** "Wow" the user immediately. High-end aesthetics (Dark Mode, Animations), simple inputs, professional results.
-   **Scope:** STRICTLY cooking/recipe generation. The system must refuse all other queries.

## 2. Technology Stack & Standards

### 2.1 Backend (Service Layer)
-   **Runtime:** Python v3.14 & Node.js v25.
-   **Architecture:** Multi-Agent System using **LangGraph** & **CrewAI**.
-   **Database:** **SQLite** (Stores approved recipes, logs, and error states).
-   **Key Constraints:**
    -   **Hallucination Control:** Mandatory validation step for all generated recipes.
    -   **Human-in-the-Loop:** If exact ingredients aren't enough, agents may suggest max 1-2 extras, but **MUST** get user approval before finalizing.
    -   **Caching:** Always check SQLite for existing recipes before querying LLM.
    -   **Retry Logic:** 3 retries max for failures. Log all errors to SQLite.

### 2.2 Frontend (Chestia-Web)
-   **Framework:** **Next.js 16** (App Router).
-   **Styling:** **Tailwind CSS v4** + Vanilla CSS for custom premium animations.
-   **Integration:** **CopilotKit** serves as a strictly passive **bridge**. It does NOT generate content; it only relays backend responses.
-   **Performance:** Follow Vercel React Best Practices (Server Components, Image Optimization).

## 3. Mandatory Development Skills & Rules

### 3.1 Test-Driven Development (TDD)
> **Rule:** *No code is written without a failing test first.*
-   **Unit Tests:** Required for all agents, utility functions, and components.
-   **Integration Tests:** Required for API endpoints and Agent-to-Database flows.
-   **Edge Cases:** Tests must cover infinite loops (approval cycles) and timeout scenarios.

### 3.2 LangChain & Software Architecture
-   **Agent Design:** Follow `langchain-architecture` patterns. Use modular Chains/Graphs.
-   **Code Quality:** Adhere to `software-architecture` principles (DRY, SOLID).
-   **Clean Code:** Meaningful variable names, consistent formatting, and self-documenting code.

### 3.3 Design & UX
-   **Aesthetics:** Strict **Dark Mode** (Deep Grays/Blacks).
-   **Interactivity:** Hover effects, micro-animations, and smooth transitions are mandatory.
-   **Language:** Documentation in English. App UI supports EN (initially) & TR.


### 3.4 Planning & Implementation Protocol
> **CRITICAL RULE:** *In PLANNING mode, no code, file, or directory changes are permitted without an approved Implementation Plan.*

1.  **Strict Planning First:**
    -   **Rule:** When in **PLANNING** mode, regardless of the user's request, **DO NOT** modify code, files, or directories directly.
    -   **Exception:** Updating `task.md` or creating the `implementation_plan.md` artifact itself.
2.  **Implementation Plan Workflow:**
    -   **Step 1:** Generate a detailed `implementation_plan.md`.
    -   **Step 2:** Request explicit User Approval.
    -   **Step 3:**
        -   *If Approved:* Proceed to EXECUTION mode and apply changes.
        -   *If Commented/Rejected:* Regnerate the implementation plan incorporating feedback and return to Step 2.
    -   **Loop:** This cycle continues until explicit approval is granted.
3.  **Deletion Safety:**
    -   **NEVER** delete a file or directory without asking for and receiving explicit user confirmation.
    -   `rm` commands or file deletion tools are strictly prohibited without prior localized approval.

### 3.5 Documentation Maintenance
-   **Rule:** Whenever any modification is made to the project (code changes, new files/directories, or deletions), the `README.md` file **MUST** be updated to reflect these changes.

## 4. Workflow Specifics

### 4.1 Recipe Generation Loop
1.  **Input:** User provides ingredients.
2.  **Check DB:** If exists -> Return Recipe.
3.  **Generate:** If not -> Agents attempt to build recipe.
    -   *Success:* Display Recipe.
    -   *Partial:* Agents propose +1/2 ingredients.
        -   *Ask User:* "Can we add X?"
        -   *Yes:* Generate & Display.
        -   *No:* Loop back for new suggestion or strict generation.
4.  **Save:** Store approved result in SQLite.

### 4.2 Error Handling
-   **Frontend:** Display "Currently unable to process your transaction" after 3 failed retries.
-   **Backend:** Log specific errors (Timeout, Hallucination, Auth) to DB.

---
*This file is to be referenced before starting any new task to ensure compliance with project standards.*
