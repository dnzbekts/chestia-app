# Product Requirements Document (PRD) - Chestia-web

## 1. Project Overview
**Chestia-web** is a conceptual single-page monolithic web application designed to solve the common culinary dilemma: "What can I cook with what I have?"
The platform serves as both a functional tool (generating recipes from inputs) and a showcase product. The design philosophy centers on a premium, minimalist, and engaging user experience that "wows" the user immediately.

## 2. Goals & Objectives
-   **User Value**: Provide immediate, creative recipe solutions based on available ingredients.
-   **Aesthetic**: Create a high-end, visual-forward interface using dark mode, rich animations, and modern typography.
-   **Accessibility**: Initially English documents/analysis, with bi-lingual support (English/Turkish) in the final product.

## 3. Technology Stack
-   **Architecture**: Monolith (Single Page Application focus initially).
-   **Front-End**:
    -   Framework: **Next.js 16** (App Router).
    -   Styling: **Tailwind CSS** (v4.0 or latest stable) + Vanilla CSS for custom animations.
    -   Language: TypeScript.
-   **Back-End** (Future Phase):
    -   Python & Node.js services (initially mocked or placeholder).
-   **Design System**: Custom premium components (Glassmorphism, Vibrant Gradients, Smooth Transitions).

## 4. Key Features (MVP)
1.  **Hero Section / Landing**:
    -   Impactful headline (e.g., "Master Your Kitchen").
    -   Dynamic visuals/backgrounds.
2.  **Smart Ingredient Input**:
    -   Interactive search bar or tag-based input for ingredients.
    -   Natural language processing (simulation for MVP).
3.  **Recipe Generation Display**:
    -   Beautifully carded recipe results.
    -   Step-by-step instructions (smooth scroll/reveal).
4.  **Localization**:
    -   Toggle between English and Turkish.

## 5. UI/UX Design Guidelines
-   **Theme**: **Strict Dark Mode**. Deep grays/blacks (`#0a0a0a`) with vibrant accent colors (Neon or Pastel contrasts).
-   **Reference**: Inspired by *eatchefly.com* but simplified and distinctive.
-   **Typography**: Clean sans-serif fonts (e.g., Inter, Outfit, or custom premium fonts).
-   **Interactivity**:
    -   Hover effects on cards.
    -   Micro-animations on buttons and inputs.
    -   No genetic stock photos; use generated or stylized artistic food imagery.

## 6. Content Strategy
-   **Tone**: Inspiring, Professional, yet Accessible.
-   **visuals**: High-contrast food photography, abstract culinary shapes.
