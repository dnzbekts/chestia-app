# Chestia Backend Integration Tests Analysis

This document details the input/output analysis and the scenarios covered by the integration tests for the Chestia Backend.

## 1. Overview
The integration tests validate the complete flow from the API layer through the LangGraph orchestration to the AI agents and database, using mocks for external dependencies (LLM) to ensure deterministic and cost-effective testing.

## 2. Test Scenarios

### 2.1 Scenario: Generate Success (Cache Hit)
- **Goal**: Verify that existing recipes are served instantly from the database.
- **Input**:
    - Endpoint: `POST /generate`
    - Payload: `{"ingredients": ["pasta", "tomato", "onion"], "difficulty": "easy", "lang": "en"}`
- **Mocking**:
    - `database.find_recipe_by_ingredients` returns a pre-defined recipe dictionary.
- **Expected Output**:
    - Status: `200 OK`
    - Content: The cached recipe object.
    - Status field: `success` (if wrapped).

### 2.2 Scenario: Generate Success (LLM Generation)
- **Goal**: Verify a cold-start generation flow where no cache exists.
- **Input**:
    - Endpoint: `POST /generate`
    - Payload: `{"ingredients": ["chicken", "rice"], "difficulty": "intermediate", "lang": "tr"}`
- **Mocking**:
    - `database.find_recipe_by_ingredients` returns `None`.
    - `RecipeAgent.generate` returns a valid recipe JSON.
    - `ReviewAgent.validate` returns `{"valid": true, "reasoning": "..."}`.
- **Expected Output**:
    - Status: `200 OK`
    - Content: `{"status": "success", "recipe": {...}, "iterations": 1, ...}` (Bilingual status).

### 2.3 Scenario: Generate with Auto-Retry (Bilingual)
- **Goal**: Verify that the system adds extra ingredients when the initial generation fails review.
- **Input**:
    - Endpoint: `POST /generate`
    - Payload: `{"ingredients": ["egg"], "difficulty": "easy", "lang": "en"}`
- **Mocking**:
    - 1st Review: `valid=False`, `suggested_extras=["milk"]`.
    - 2nd Generation: Receives `["egg", "milk"]`.
    - 2nd Review: `valid=True`.
- **Expected Output**:
    - Status: `200 OK`
    - Content: Recipe including `milk`, `extra_ingredients_added=["milk"]`, `iterations=2`.

### 2.4 Scenario: Generate Failure (Strict Constraints)
- **Goal**: Verify bilingual error message when max iterations/extras are reached.
- **Input**:
    - Endpoint: `POST /generate`
    - Payload: `{"ingredients": ["stone"], "difficulty": "hard", "lang": "tr"}`
- **Mocking**:
    - Agent returns invalid recipes or Reviewer suggests extras that still fail.
- **Expected Output**:
    - Status: `200 OK` (with status "error") or appropriate error code.
    - Message (TR): "İlettiğiniz malzemelerle uygun bir tarif bulunamadı..."
    - Message (EN): "No suitable recipe could be found..."

### 2.5 Scenario: Validation Failure (Bilingual)
- **Goal**: Verify rejection of insufficient or default-only ingredients.
- **Input**:
    - Payload: `{"ingredients": ["salt", "water", "oil"], "difficulty": "easy", "lang": "en"}`
- **Expected Output**:
    - Status: `422 Unprocessable Entity`
    - Detail: "At least one non-default ingredient is required (ingredients like water, salt, and oil do not count)"

### 2.6 Scenario: Modify Recipe
- **Goal**: Verify the modification flow with user notes.
- **Input**:
    - Endpoint: `POST /modify`
    - Payload: `{"original_ingredients": ["pasta"], "new_ingredients": ["cream"], "difficulty": "hard", "modification_note": "make it spicy", "lang": "en"}`
- **Mocking**:
    - LLM generation taking the note into account.
- **Expected Output**:
    - Status: `200 OK`
    - Content: New recipe reflecting changes.

### 2.7 Scenario: Feedback & Caching
- **Goal**: Verify that approved recipes are persisted.
- **Input**:
    - Endpoint: `POST /feedback`
    - Payload: `{"ingredients": ["pasta"], "difficulty": "easy", "approved": true, "recipe": {...}}`
- **Expected Output**:
    - Status: `200 OK`
    - Database: New record in `recipes` table.

## 3. Bilingual Support Matrix

| Key | English Message | Turkish Message |
|-----|-----------------|-----------------|
| min_ingredients | At least one non-default ingredient is required... | En az bir adet default olmayan malzeme gerekli... |
| recipe_not_found | No suitable recipe could be found... | İlettiğiniz malzemelerle uygun bir tarif bulunamadı... |
| generation_error | Unable to process your request at this time | Şu anda isteğiniz işlenemiyor |
| feedback_saved | Recipe saved successfully | Tarif başarıyla kaydedildi |
| feedback_rejected| Please try again with different ingredients | Farklı malzemelerle tekrar deneyin |
