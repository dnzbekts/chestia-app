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

    def generate(self, ingredients: List[str]) -> Dict[str, Any]:
        ingredients = self._sanitize_ingredients(ingredients)
        if not ingredients:
            raise ValueError("No valid ingredients provided after sanitization")
        
        prompt = f"Create a recipe with these ingredients: {', '.join(ingredients)}. Return JSON with name, ingredients, steps, metadata."
        
        response = self.llm.invoke(prompt)
        
        try:
            # Simple cleanup for markdown code blocks if any
            content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except json.JSONDecodeError:
            # In a real app we might retry or return structure err
            # For this MVP/test, we return what we got if check fails, but simpler to raise or return error dict
            return {"error": "Invalid JSON", "raw": response.content}
