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

    def validate(self, recipe: Dict[str, Any], user_ingredients: List[str]) -> Dict[str, Any]:
        """Validate recipe for hallucinations and logic Errors"""
        
        prompt = f"""
        Role: Senior Culinary Reviewer
        Task: Validate if the generated recipe is logically sound and uses ONLY the provided ingredients or a maximum of 1-2 common base ingredients (like water, salt, oil) if absolutely necessary.
        
        User Ingredients: {', '.join(user_ingredients)}
        
        Generated Recipe:
        Name: {recipe.get('name')}
        Ingredients: {', '.join(recipe.get('ingredients', []))}
        Steps: {', '.join(recipe.get('steps', []))}
        
        Requirements:
        1. Does it use ingredients NOT in the user list (excluding basics like water/salt/oil)?
        2. Are the steps logical for these ingredients?
        3. Is it a real cooking recipe?
        
        Return JSON in this format:
        {{
            "valid": boolean,
            "reasoning": "Detailed explanation of why it is valid or invalid"
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
