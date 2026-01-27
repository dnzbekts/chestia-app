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
            model="gemini-1.5-flash", 
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
        Task: Validate if the generated recipe is logically sound and matches difficulty.
        
        User Ingredients: {', '.join(user_ingredients)}
        Requested Difficulty: {difficulty}
        
        DEFAULT INGREDIENTS (assumed available in every household, don't count as extras):
        {default_ingredients_list}
        
        Generated Recipe:
        Name: {recipe.get('name')}
        Ingredients: {', '.join(recipe.get('ingredients', []))}
        Steps: {', '.join(recipe.get('steps', []))}
        
        Requirements:
        1. Recipe MAY freely use any DEFAULT ingredients (water, oil, salt, sugar, spices like pepper, paprika, cumin, etc.)
        2. Recipe should primarily use the user-provided ingredients
        3. If recipe uses NON-DEFAULT ingredients NOT in the user list, mark as INVALID
        4. Are the steps logical for these ingredients?
        5. Is this a real cooking recipe?
        6. NEW: Does recipe complexity match {difficulty} difficulty?
           - Easy: Simple steps, minimal technique
           - Intermediate: Moderate complexity, some skill needed
           - Hard: Advanced techniques, precise execution
        
        Return JSON in this format:
        {{
            "valid": boolean,
            "reasoning": "Detailed explanation of why it is valid or invalid, including difficulty assessment"
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
