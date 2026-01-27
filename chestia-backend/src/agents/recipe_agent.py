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
        
        AVAILABLE INGREDIENTS:
        - User's Ingredients: {', '.join(ingredients)}
        - Default Ingredients (always available): {default_ingredients_list}
        
        Difficulty Level: {difficulty.upper()} - {difficulty_guidance.get(difficulty, '')}
        
        STRICT RULES (MUST FOLLOW):
        1. You MUST ONLY use ingredients from the lists above
        2. Do NOT add ANY ingredient that is not in User's Ingredients or Default Ingredients
        3. This is a hard constraint - violation means the recipe is invalid
        
        Recipe Guidelines:
        1. Create a {difficulty} difficulty recipe using ONLY the available ingredients
        2. Match complexity to {difficulty} level:
           - Easy: Simple steps, basic techniques, 15-30 min
           - Intermediate: Multiple steps, some technique required, 30-60 min
           - Hard: Complex techniques, multiple stages, 60+ min
        
        Return JSON:
        {{
            "name": "Recipe Name (Turkish or English)",
            "ingredients": ["only ingredients from available lists"],
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
