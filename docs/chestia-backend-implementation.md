# Chestia Backend Implementation Guide for Frontend

This document provides a comprehensive guide for integrating the `chestia-web` frontend with the `chestia-backend`. It details the CopilotKit integration, API endpoints, and data structures.

## 🔗 CopilotKit Integration (Primary Method)

The primary method for frontend-backend communication is via the CopilotKit SDK using the AG-UI protocol.

### Remote Endpoint
- **URL**: `/copilotkit` (Relative to backend base URL, e.g., `http://localhost:8000/copilotkit`)
- **Type**: `CopilotKitRemoteEndpoint`
- **Method**: `POST` (Managed by SDK)

### Agent Configuration
- **Agent Name**: `chestia_recipe_agent`
- **Description**: "Intelligent recipe generation using strict ingredient constraints. Prioritizes local cache, then Tavily web search, and falls back to Gemini AI generation with auto-retry and validation."

### 🧠 Recipe Resolution Strategy
The backend employs a 3-tier strategy to find the best recipe:
1.  **Cache Hit**: Checks SQLite database for existing valid recipes.
2.  **Web Search (Tavily)**: If cache miss, searches the web for a matching recipe using *only* the provided ingredients.
3.  **GenAI Fallback**: If web search fails, generates a new recipe using Google Gemini with strict ingredient adherence.

### State Schema (`CopilotKitState`)

The frontend must sync with this state structure.

| Field | Type | Description |
|-------|------|-------------|
| `messages` | `BaseMessage[]` | Chat history (User/AI messages). |
| `ingredients` | `string[]` | List of user's filtered ingredients. |
| `difficulty` | `string` | "easy", "intermediate", or "hard". |
| `lang` | `string` | "en" or "tr". |
| `recipe` | `object` | Generated recipe (null if not ready). |
| `extra_ingredients` | `string[]` | Ingredients suggested by AI during retries. |
| `extra_count` | `number` | Count of extras added (max 2). |
| `error` | `string` | Error message if generation fails. |
| `iteration_count` | `number` | Current retry iteration (max 3). |

#### Recipe Object Structure
```json
{
  "name": "Recipe Name",
  "ingredients": ["ing1", "ing2", ...],
  "steps": ["Step 1", ...],
  "metadata": {
    "cooking_time": "30 min",
    "difficulty": "easy"
  }
}
```

---

## 📡 REST API Endpoints (Legacy/Direct Support)

These endpoints are available for direct access outside of the CopilotKit flow.

### 1. Generate Recipe
**POST** `/generate`

**Request Body:**
```json
{
  "ingredients": ["chicken", "rice"],
  "difficulty": "easy",
  "lang": "en"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "recipe": { ... },
  "extra_ingredients_added": [],
  "iterations": 1
}
```

### 2. Modify Recipe
**POST** `/modify`

**Request Body:**
```json
{
  "original_ingredients": ["chicken", "rice"],
  "new_ingredients": ["tomato"],
  "difficulty": "intermediate",
  "modification_note": "make it spicy",
  "lang": "en"
}
```

### 3. Submit Feedback
**POST** `/feedback`

**Request Body:**
```json
{
  "ingredients": ["chicken", "rice"],
  "difficulty": "easy",
  "approved": true,
  "recipe": { ... },
  "lang": "en"
}
```

---

## ⚠️ Error Handling

- **422 Unprocessable Entity**: Invalid input (e.g., fewer than 3 ingredients, invalid characters).
- **500 Internal Server Error**: Unexpected backend failures (masked in production).

## 🌍 Internationalization

- Include `"lang": "tr"` in requests to receive error messages and recipe content in Turkish.
- Default language is `"en"`.
