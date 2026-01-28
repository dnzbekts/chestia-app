from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import json

load_dotenv()

class ReviewAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "YOUR_KEY_HERE":
            raise RuntimeError("GOOGLE_API_KEY is not set in environment variables")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            google_api_key=api_key,
            temperature=0
        )

    def validate(self, recipe: Dict[str, Any], user_ingredients: List[str], difficulty: str) -> Dict[str, Any]:
        """
        Validate recipe for hallucinations, logic errors, and difficulty match.
        
        Args:
            recipe: Generated recipe to validate
            user_ingredients: Original user-provided ingredients
            difficulty: Requested difficulty level
        """
        from config import DEFAULT_INGREDIENTS
        
        # Format default ingredients list for prompt
        default_ingredients_list = ', '.join(sorted(DEFAULT_INGREDIENTS))
        
        prompt = f"""
        Role: Senior Culinary Reviewer
        Task: Validate recipe and suggest improvements if invalid.
        
        User Ingredients: {', '.join(user_ingredients)}
        Requested Difficulty: {difficulty}
        
        DEFAULT INGREDIENTS (always available, don't count as extras):
        {default_ingredients_list}
        
        Generated Recipe:
        Name: {recipe.get('name')}
        Ingredients: {', '.join(recipe.get('ingredients', []))}
        Steps: {', '.join(recipe.get('steps', []))}
        
        VALIDATION RULES:
        1. Recipe MAY use any DEFAULT ingredients freely
        2. Recipe MUST primarily use User Ingredients
        3. If recipe uses NON-DEFAULT ingredients NOT in user list -> INVALID
        4. Steps must be logical and achievable
        5. Must be a real, edible recipe
        6. Complexity must match {difficulty}:
           - Easy: Simple steps, minimal technique
           - Intermediate: Moderate complexity
           - Hard: Advanced techniques
        
        IMPORTANT: If the recipe is INVALID, suggest 1-2 common ingredients that could help create a valid recipe.
        
        Return JSON:
        {{
            "valid": true/false,
            "reasoning": "Detailed explanation including difficulty assessment",
            "suggested_extras": ["ingredient1", "ingredient2"]  // Only if invalid, max 2 suggestions
        }}
        """
        
        response = self.llm.invoke(prompt)
        
        try:
            content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "valid": False,
                "reasoning": "Reviewer failed to provide a valid JSON response."
            }
