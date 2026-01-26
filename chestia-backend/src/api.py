from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
import json
import re
from graph import create_graph
from database import get_db_connection, init_db, log_error

app = FastAPI(title="Chestia Backend")

# Initialize the graph
graph = create_graph()

class GenerateRequest(BaseModel):
    ingredients: List[str] = Field(..., min_items=1, max_items=20)

    @validator('ingredients', each_item=True)
    def validate_ingredient_chars(cls, v):
        if not re.match(r"^[a-zA-Z0-9\s,-]+$", v):
            raise ValueError("Ingredient contains invalid characters")
        if len(v) > 50:
            raise ValueError("Ingredient name too long")
        return v

class FeedbackRequest(BaseModel):
    ingredients: List[str]
    approved: bool
    recipe: Dict[str, Any]

@app.post("/generate")
def generate_recipe(request: GenerateRequest):
    try:
        # Initial state
        initial_state = {
            "ingredients": request.ingredients, 
            "recipe": None, 
            "error": None,
            "needs_approval": False,
            "extra_ingredients": [],
            "iteration_count": 0
        }
        result = graph.invoke(initial_state)
        
        # If the graph needs approval, return the intermediate state
        if result.get("needs_approval"):
            return {
                "status": "needs_approval",
                "recipe": result.get("recipe"),
                "reasoning": result.get("error")
            }
            
        if result.get("error") and not result.get("recipe"):
            # Log error to DB
            conn = get_db_connection()
            log_error(conn, "GenerationError", result["error"])
            conn.close()
            # Generic error for the user
            raise HTTPException(status_code=500, detail="Unable to process your request at this time")
            
        return result.get("recipe", {})
    except HTTPException:
        raise
    except Exception as e:
        conn = get_db_connection()
        log_error(conn, "UnexpectedError", str(e))
        conn.close()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/feedback")
def handle_feedback(request: FeedbackRequest):
    """Handle user approval or rejection of suggested ingredients"""
    if not request.approved:
        return {"status": "rejected", "message": "Please provide different ingredients."}
    
    # If approved, we save to DB and return success
    conn = get_db_connection()
    try:
        init_db(conn) # Ensure tables exist
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO recipes (name, ingredients, steps, metadata)
            VALUES (?, ?, ?, ?)
        """, (
            request.recipe["name"], 
            json.dumps(sorted(request.ingredients)), 
            json.dumps(request.recipe["steps"]), 
            json.dumps(request.recipe.get("metadata", {}))
        ))
        conn.commit()
        return {"status": "success", "recipe": request.recipe}
    except Exception as e:
        log_error(conn, "FeedbackError", str(e))
        raise HTTPException(status_code=500, detail="Failed to save your feedback")
    finally:
        conn.close()
