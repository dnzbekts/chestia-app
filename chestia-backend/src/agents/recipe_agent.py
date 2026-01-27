from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import json

load_dotenv()

class RecipeInput(BaseModel):
    ingredients: List[str]

class RecipeAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "YOUR_KEY_HERE":
            raise RuntimeError("GOOGLE_API_KEY is not set in environment variables")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            google_api_key=api_key,
            temperature=0.7
        )

    def _sanitize_ingredients(self, ingredients: List[str]) -> List[str]:
        """Strict input validation for ingredients"""
        sanitized = []
        for ing in ingredients:
            # Remove any non-alphanumeric chars except space/comma
            clean = "".join(char for char in ing if char.isalnum() or char in " ,-").strip()
            if clean and len(clean) < 50:
                sanitized.append(clean)
        return sanitized

    def generate(self, ingredients: List[str], difficulty: str) -> Dict[str, Any]:
        """
        Generate a recipe from user-provided ingredients at specified difficulty.
        Default household ingredients are assumed available.
        
        Args:
            ingredients: User's ingredient list
            difficulty: Recipe difficulty ('easy', 'intermediate', 'hard')
        """
        from config import DEFAULT_INGREDIENTS
        
        ingredients = self._sanitize_ingredients(ingredients)
        if not ingredients:
            raise ValueError("No valid ingredients provided after sanitization")
        
        # Format default ingredients for prompt
        default_ingredients_list = ', '.join(sorted(DEFAULT_INGREDIENTS))
        
        # Difficulty-specific instructions
        difficulty_guidance = {
            "easy": "Simple techniques, minimal prep, 15-30 min total time, beginner-friendly",
            "intermediate": "Moderate techniques, some prep required, 30-60 min, home cook level",
            "hard": "Advanced techniques, significant prep, 60+ min, experienced cook level"
        }
        
        prompt = f"""
        You are a professional chef creating a recipe.
        
        User's Ingredients: {', '.join(ingredients)}
        Difficulty Level: {difficulty.upper()} - {difficulty_guidance.get(difficulty, '')}
        
        DEFAULT INGREDIENTS (assumed available, use freely):
        {default_ingredients_list}
        
        Instructions:
        1. Create a {difficulty} difficulty recipe primarily using the user's ingredients
        2. You MAY use any default ingredients (water, oil, salt, sugar, spices) without restriction
        3. Try to avoid suggesting additional non-default ingredients
        4. Adjust recipe complexity to match {difficulty} level:
           - Easy: Simple steps, basic techniques
           - Intermediate: Multiple steps, some technique required
           - Hard: Complex techniques, multiple stages, precise timing
        
        Return JSON with this structure:
        {{
            "name": "Recipe Name",
            "ingredients": ["ingredient1", "ingredient2", ...],
            "steps": ["step1", "step2", ...],
            "metadata": {{"time": "20min", "difficulty": "{difficulty}"}}
        }}
        """
        
        response = self.llm.invoke(prompt)
        
        try:
            content = response.content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(content)
            return parsed
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse recipe JSON: {e}")
        
        response = self.llm.invoke(prompt)
        
        try:
            # Simple cleanup for markdown code blocks if any
            content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except json.JSONDecodeError:
            # In a real app we might retry or return structure err
            # For this MVP/test, we return what we got if check fails, but simpler to raise or return error dict
            return {"error": "Invalid JSON", "raw": response.content}
