# Chestia Backend Integration Guide

This document details the backend architecture for the Chestia project and provides a comprehensive guide for integrating the CopilotKit frontend.

## 1. Backend Server Architecture

The `chestia-backend` is a sophisticated **Multi-Agent System** acting as the reasoning engine for the Chestia culinary platform.

### 1.1 Core Technologies

- **Runtime**: Python 3.12+ (FastAPI)
- **Orchestration**: LangGraph (Stateful Agent Workflow)
- **Integration**: `ag_ui_langgraph` (CopilotKit <-> LangGraph Bridge)
- **Persistence**: SQLite (Recipes, Logs) + MemorySaver (Agent State/Threads)

### 1.2 The Agentic Workflow

The system uses a graph-based workflow (`src/workflow/graph.py`) where specialized agents collaborate to generate recipes.

**Nodes (Agents):**

1. **`validate_ingredients`**: Sanitizes input and checks constraints (min 2 ingredients).
2. **`search_cache`**: Checks SQLite for existing approved recipes (fast retrieval).
3. **`semantic_search`**: Uses vector embeddings to find similar recipes (fuzzy retrieval).
4. **`web_search`**: Queries Tavily for real-world recipes (if cache misses).
5. **`generate_recipe`**: Uses LLM (Gemini/OpenAI) to invent a recipe if no external source is found.
6. **`review_recipe`**: self-correction loop where an agent critiques the generated recipe and suggests improvements or extra ingredients.

### 1.3 State Management

The graph uses a shared state object `GraphState` that inherits from `CopilotKitState`. This ensures perfect synchronization between the Python backend and the React frontend.

```python
class GraphState(CopilotKitState):
    ingredients: List[str]
    recipes: Optional[Dict]
    # ... other fields ...
```

### 1.4 API Endpoints

The backend exposes a unified endpoint for CopilotKit to communicate with the LangGraph agent.

- **Base URL**: `http://localhost:8000`
- **Integration Endpoint**: `/copilotkit` (POST) determines the action.
- **Health Check**: `/copilotkit/health` (GET) returns agent status.

---

## 2. Frontend Integration Guide (Chestia-Web)

This section outlines the steps to connect the Next.js frontend to the backend using CopilotKit.

 > [!IMPORTANT]
 > **Do NOT start coding yet.** This guide is for reference when you begin the frontend integration task.

### 2.1 Prerequisites

Ensure the following packages are installed (already done in previous steps, but verify):

```bash
npm install @copilotkit/react-core @copilotkit/react-ui @copilotkit/runtime
```

### 2.2 Environment Configuration

Add the backend URL to your `.env.local` file in `chestia-web`:

```bash
# Point to your local FastAPI backend
LANGGRAPH_DEPLOYMENT_URL="http://127.0.0.1:8000/copilotkit"
```

### 2.3 Create the API Route

You need a Next.js API route that acts as a proxy between the client and the LangGraph agent.

**File:** `app/api/copilotkit/route.ts`

```typescript
import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { LangGraphHttpAgent } from "@copilotkit/runtime/langgraph"; // Note: HttpAgent for remote
import { NextRequest } from "next/server";

const serviceAdapter = new ExperimentalEmptyAdapter();

const runtime = new CopilotRuntime({
  agents: {
    chestia_agent: new LangGraphHttpAgent({
      name: "chestia_backend_agent",
      url: process.env.LANGGRAPH_DEPLOYMENT_URL || "http://127.0.0.1:8000/copilotkit",
    }),
  }
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};
```

### 2.4 Configure the Provider

Wrap your application layout with `CopilotKit`.

**File:** `app/layout.tsx`

```tsx
import { CopilotKit } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css"; 

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <CopilotKit runtimeUrl="/api/copilotkit" agent="chestia_agent">
            {children}
        </CopilotKit>
      </body>
    </html>
  );
}
```

### 2.5 Add the Chat UI

Use the `CopilotSidebar` or `CopilotPopup` to interact with the agent.

**File:** `app/page.tsx` (or your main layout)

```tsx
import { CopilotSidebar } from "@copilotkit/react-ui";

export default function Page() {
  return (
    <>
      {/* Your main content */}
      <CopilotSidebar 
        instructions="You are a helpful culinary assistant."
        defaultOpen={true}
        labels={{
            title: "Chef Chestia",
            initial: "Hi! integration is ready. What ingredients do you have?"
        }}
      />
    </>
  );
}
```

---

## 3. Vercel & React Best Practices Checklist

When implementing the frontend, strictly adhere to the following **Vercel React Best Practices** to ensure performance and maintainability.

### ⚡️ Performance (Critical)

- **Eliminate Waterfalls**: Do not nest `await` calls unnecessarily. Use `Promise.all` for independent data fetching.
- **Bundle Size**:
  - Avoid "Barrel Files" (e.g., `import { X } from './components'`). Instead import directly: `import { X } from './components/X'`.
  - Use `next/dynamic` for heavy components (e.g., complex charts or heavy UI libraries) to lazy load them.

### Rendering & Re-renders

- **Conditional Rendering**: Use Ternary Operators (`condition ? <A /> : <B />`) instead of `&&` short-circuiting (`condition && <A />`) to avoid rendering `0` or empty strings unexpectedly.
- **Interaction**: Use `startTransition` for non-urgent state updates that don't need to block the UI.

### Server Components

- **Server-First**: Keep components as **Server Components** by default. Only add `"use client"` when you absolutely need interactivity (hooks like `useState`, `useEffect`).
- **Serialization**: Pass only serializable data (JSON-compatible) from Server to Client components. Avoid passing functions or class instances.

By following this guide, you will ensure a robust, high-performance integration between the Chestia intelligent backend and the React frontend.
