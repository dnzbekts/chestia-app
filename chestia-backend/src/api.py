from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Literal
import json
import re
from graph import create_graph
from database import get_db_connection, init_db, log_error, save_recipe
from config import filter_default_ingredients, COPILOTKIT_AGENT_NAME, COPILOTKIT_AGENT_DESCRIPTION
from utils import i18n

# CopilotKit imports
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAGUIAgent
from copilotkit_agent import copilotkit_graph

app = FastAPI(title="Chestia Backend")

# Initialize the graph
graph = create_graph()

# Initialize CopilotKit Remote Endpoint with LangGraph AGUI agent
copilotkit_sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAGUIAgent(
            name=COPILOTKIT_AGENT_NAME,
            description=COPILOTKIT_AGENT_DESCRIPTION,
            graph=copilotkit_graph,
        )
    ],
)

# Add CopilotKit endpoint to FastAPI
add_fastapi_endpoint(app, copilotkit_sdk, "/copilotkit")


class GenerateRequest(BaseModel):
    ingredients: List[str] = Field(..., min_length=3, max_length=20)
    difficulty: Literal["easy", "intermediate", "hard"] = Field(
        ...,
        description="Recipe difficulty level: easy, intermediate, or hard"
    )
    lang: Literal["tr", "en"] = Field("en", description="Preferred language for messages: tr or en")

    @validator('ingredients', each_item=True)
    def validate_ingredient_chars(cls, v):
        if not re.match(r"^[a-zA-Z0-9\s,\-çÇğĞıİöÖşŞüÜ]+$", v):
            raise ValueError("Ingredient contains invalid characters")
        if len(v) > 50:
            raise ValueError("Ingredient name too long")
        return v


class ModifyRequest(BaseModel):
    """Request to modify/regenerate a recipe"""
    original_ingredients: List[str] = Field(..., min_length=3, max_length=20)
    new_ingredients: Optional[List[str]] = Field(None, max_length=20)
    difficulty: Literal["easy", "intermediate", "hard"]
    modification_note: Optional[str] = None  # e.g., "make it spicier"
    lang: Literal["tr", "en"] = Field("en", description="Preferred language for messages")
    
    @validator('original_ingredients', 'new_ingredients', each_item=True)
    def validate_ingredient_chars(cls, v):
        if v is None:
            return v
        if not re.match(r"^[a-zA-Z0-9\s,\-çÇğĞıİöÖşŞüÜ]+$", v):
            raise ValueError("Ingredient contains invalid characters")
        if len(v) > 50:
            raise ValueError("Ingredient name too long")
        return v


class FeedbackRequest(BaseModel):
    ingredients: List[str]
    difficulty: str
    approved: bool
    recipe: Dict[str, Any]
    lang: Literal["tr", "en"] = Field("en")


@app.post("/generate")
def generate_recipe(request: GenerateRequest):
    """
    Generate a recipe from ingredients.
    
    Flow:
    1. Filter out default ingredients (salt, water, oil, etc.)
    2. If no non-default ingredients remain, return error
    3. Invoke graph with filtered ingredients
    4. Graph auto-retries up to 3 times, adding max 2 extras if needed
    5. Return final recipe or error
    """
    try:
        # Step 1: Filter default ingredients BEFORE graph
        filtered_ingredients = filter_default_ingredients(request.ingredients)
        
        # Step 2: Validate at least 1 non-default ingredient
        if len(filtered_ingredients) < 1:
            raise HTTPException(
                status_code=422, 
                detail=i18n.get_message(i18n.MIN_INGREDIENTS, request.lang)
            )
        
        # Step 3: Invoke graph with filtered ingredients
        result = graph.invoke({
            "ingredients": filtered_ingredients,
            "original_ingredients": request.ingredients,  # Keep originals for reference
            "difficulty": request.difficulty,
            "lang": request.lang,
            "recipe": None,
            "extra_ingredients": [],
            "extra_count": 0,
            "error": None,
            "iteration_count": 0
        })

        if result and result.get("recipe"):
            conn = get_db_connection()
            init_db(conn)
            save_recipe(
                conn,
                name=result["recipe"]["name"],
                ingredients=filtered_ingredients,
                difficulty=request.difficulty,
                steps=result["recipe"]["steps"],
                metadata=result["recipe"].get("metadata", {})
            )
            conn.close()
        
        # Step 4: Handle result - no more needs_approval flow
        if result.get("error"):
            # Log error to DB
            conn = get_db_connection()
            log_error(conn, "GenerationError", result["error"])
            conn.close()
            
            # Return user-friendly error
            return {
                "status": "error",
                "message": result["error"],
                "extra_ingredients_tried": result.get("extra_ingredients", [])
            }
        
        # Step 5: Return successful recipe
        recipe = result.get("recipe", {})
        return {
            "status": "success",
            "recipe": recipe,
            "extra_ingredients_added": result.get("extra_ingredients", []),
            "iterations": result.get("iteration_count", 1)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn = get_db_connection()
        log_error(conn, "UnexpectedError", str(e))
        conn.close()
        raise HTTPException(
            status_code=500, 
            detail=i18n.get_message(i18n.INTERNAL_SERVER_ERROR, request.lang)
        )


@app.post("/modify")
def modify_recipe(request: ModifyRequest):
    """
    Modify or regenerate a recipe with updated ingredients.
        
    Use cases:
    - User didn't like the recipe, wants a different one
    - User wants to add new ingredients
    - User wants to change difficulty
    """
    try:
        # Combine original + new ingredients
        all_ingredients = list(request.original_ingredients)
        if request.new_ingredients:
            all_ingredients.extend(request.new_ingredients)
        
        # Filter defaults
        filtered_ingredients = filter_default_ingredients(all_ingredients)
        
        if len(filtered_ingredients) < 1:
            raise HTTPException(
                status_code=422,
                detail=i18n.get_message(i18n.MIN_INGREDIENTS, request.lang)
            )
        
        # Invoke graph - starts fresh with new ingredient list
        result = graph.invoke({
            "ingredients": filtered_ingredients,
            "original_ingredients": all_ingredients,
            "difficulty": request.difficulty,
            "lang": request.lang,
            "recipe": None,
            "extra_ingredients": [],
            "extra_count": 0,
            "error": None,
            "iteration_count": 0
        })
        if result and result.get("recipe"):
            conn = get_db_connection()
            init_db(conn)
            save_recipe(
                conn,
                name=result["recipe"]["name"],
                ingredients=filtered_ingredients,
                difficulty=request.difficulty,
                steps=result["recipe"]["steps"],
                metadata=result["recipe"].get("metadata", {})
            )
            conn.close()
        
        if result.get("error"):
            conn = get_db_connection()
            log_error(conn, "ModificationError", result["error"])
            conn.close()
            
            return {
                "status": "error",
                "message": result["error"]
            }
        
        return {
            "status": "success",
            "recipe": result.get("recipe", {}),
            "extra_ingredients_added": result.get("extra_ingredients", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn = get_db_connection()
        log_error(conn, "UnexpectedError", str(e))
        conn.close()
        raise HTTPException(
            status_code=500, 
            detail=i18n.get_message(i18n.INTERNAL_SERVER_ERROR, request.lang)
        )


@app.post("/feedback")
def handle_feedback(request: FeedbackRequest):
    """Cache approved recipes for future use"""
    if not request.approved:
        return {
            "status": "rejected", 
            "message": i18n.get_message(i18n.FEEDBACK_REJECTED, request.lang)
        }
    
    conn = get_db_connection()
    try:
        init_db(conn)
        
        # Filter default ingredients before caching
        non_default_ingredients = filter_default_ingredients(request.ingredients)
        
        save_recipe(
            conn,
            name=request.recipe["name"],
            ingredients=non_default_ingredients,
            difficulty=request.difficulty,
            steps=request.recipe["steps"],
            metadata=request.recipe.get("metadata", {})
        )
        
        return {
            "status": "success", 
            "recipe": request.recipe,
            "message": i18n.get_message(i18n.FEEDBACK_SUCCESS, request.lang)
        }
    except Exception as e:
        log_error(conn, "FeedbackError", str(e))
        raise HTTPException(
            status_code=500, 
            detail=i18n.get_message(i18n.FEEDBACK_SAVE_FAILED, request.lang)
        )
    finally:
        conn.close()
