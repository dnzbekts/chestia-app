from langchain_tavily import TavilySearch
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Optional, Dict, Any
import os
import json
from config import DEFAULT_INGREDIENTS

class SearchAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "YOUR_KEY_HERE":
            raise RuntimeError("GOOGLE_API_KEY is not set")

        search_api_key = os.getenv("TAVILY_API_KEY")
        if not search_api_key or search_api_key == "YOUR_KEY_HERE":
            raise RuntimeError("TAVILY_API_KEY is not set")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.1 # Low temp for parsing
        )
        
        # Initialize Tavily tool
        # Ensure TAVILY_API_KEY is in env or passed explicitly
        self.search_tool = TavilySearch(
            max_results=3,
            search_depth="advanced",
            api_key=search_api_key
        )

    def search(self, ingredients: List[str], difficulty: str) -> Optional[Dict[str, Any]]:
        """
        Search for a recipe using ingredients and return structured data.
        Returns None if no suitable recipe found.
        """
        # 1. Construct strict query
        default_ing_str = ", ".join(sorted(DEFAULT_INGREDIENTS))
        user_ing_str = ", ".join(ingredients)
        
        query = f"recipe using ONLY {user_ing_str} (pantry: {default_ing_str}) difficulty {difficulty} full recipe steps"
        
        try:
            # 2. Execute Search
            results = self.search_tool.invoke({"query": query})
            
            if not results or not isinstance(results, list):
                return None
                
            # Combine content for parsing
            context = "\n\n".join([r.get("content", "") for r in results])
            
            # 3. Parse with LLM
            parse_prompt = f"""
            You are a recipe parser. Extract a SINGLE recipe from the search results below.
            
            CONSTRAINTS:
            - The recipe MUST use predominantly the user's ingredients: {user_ing_str}
            - Allowed pantry items: {default_ing_str}
            - If the search results do not contain a COMPLETE recipe that fits these ingredients, return "NO_RECIPE".
            - Do not invent a recipe. Only extract what is found.
            
            SEARCH RESULTS:
            {context}
            
            OUTPUT FORMAT (JSON ONLY):
            {{
                "name": "Recipe Name",
                "ingredients": ["list", "of", "ingredients"],
                "steps": ["step 1", "step 2"],
                "metadata": {{"difficulty": "{difficulty}", "source": "web_search"}}
            }}
            
            If valid recipe found, return JSON. Else return "NO_RECIPE".
            """
            
            response = self.llm.invoke(parse_prompt)
            content = response.content.strip().replace("```json", "").replace("```", "")
            
            if "NO_RECIPE" in content or not content:
                return None
                
            recipe = json.loads(content)
            
            # Basic validation
            if not recipe.get("steps") or not recipe.get("ingredients"):
                return None
                
            return recipe
            
        except Exception as e:
            print(f"Search failed: {e}")
            return None
