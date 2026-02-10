from fastapi import APIRouter, HTTPException, Request
import logging

# CopilotKit Imports
from copilotkit import LangGraphAGUIAgent
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from src.workflow.graph import create_workflow_graph

from src.api.schemas import GenerateRequest, ModifyRequest, FeedbackRequest
from src.api.rate_limit import limiter
from src.workflow import create_graph
from src.services import get_recipe_service
from src.domain import filter_default_ingredients
from src.infrastructure.localization import i18n
from src.workflow.graph import create_graph

logger = logging.getLogger(__name__)

router = APIRouter()

# CopilotKit Configuration
agent = LangGraphAGUIAgent(
    name="chestia_backend_agent",
    description="A culinary agent that generates recipes from ingredients.",
    graph=create_workflow_graph(),
)

add_langgraph_fastapi_endpoint(router, agent, "/copilotkit")

# Initialize the graph
graph = create_graph()


@router.post("/generate")
@limiter.limit("5/minute")
def generate_recipe(payload: GenerateRequest, request: Request):
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
        filtered_ingredients = filter_default_ingredients(payload.ingredients)
        
        # Step 2: Validate at least 2 non-default ingredient
        if len(filtered_ingredients) < 2:
            raise HTTPException(
                status_code=422, 
                detail=i18n.get_message(i18n.MIN_INGREDIENTS, payload.lang)
            )
        
        # Step 3: Invoke graph with filtered ingredients
        result = graph.invoke({
            "ingredients": filtered_ingredients,
            "original_ingredients": payload.ingredients,  # Keep originals for reference
            "difficulty": payload.difficulty,
            "lang": payload.lang,
            "recipe": None,
            "extra_ingredients": [],
            "extra_count": 0,
            "error": None,
            "iteration_count": 0,
            "source_node": None
        })

        # Save only newly generated or web-searched recipes (not cache/semantic hits)
        source_node = result.get("source_node", "unknown")
        if result and result.get("recipe"):
            recipe_service = get_recipe_service()
            recipe_service.save_generated_recipe(
                recipe=result["recipe"],
                ingredients=result["ingredients"],
                difficulty=result.get("difficulty", payload.difficulty),
                lang=result.get("lang", payload.lang),
                source_node=source_node
            )
        
        # Step 4: Handle result
        if result.get("error"):
            # Log error to DB
            recipe_service = get_recipe_service()
            recipe_service.log_error("GenerationError", result["error"])
            
            logger.warning(f"Recipe generation error: {result['error']}")
            
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
            "source_node": result.get("source_node", "unknown"),
            "extra_ingredients_added": result.get("extra_ingredients", []),
            "iterations": result.get("iteration_count", 1)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_recipe: {e}", exc_info=True)
        recipe_service = get_recipe_service()
        recipe_service.log_error("UnexpectedError", str(e))
        raise HTTPException(
            status_code=500, 
            detail="An internal error occurred while processing the recipe."
        )


@router.post("/modify")
@limiter.limit("5/minute")
def modify_recipe(payload: ModifyRequest, request: Request):
    """
    Modify or regenerate a recipe with updated ingredients.
        
    Use cases:
    - User didn't like the recipe, wants a different one
    - User wants to add new ingredients
    - User wants to change difficulty
    """
    try:
        # Combine original + new ingredients
        all_ingredients = list(payload.original_ingredients)
        if payload.new_ingredients:
            all_ingredients.extend(payload.new_ingredients)
        
        # Filter defaults
        filtered_ingredients = filter_default_ingredients(all_ingredients)
        
        if len(filtered_ingredients) < 2:
            raise HTTPException(
                status_code=422,
                detail=i18n.get_message(i18n.MIN_INGREDIENTS, payload.lang)
            )
        
        # Invoke graph - starts fresh with new ingredient list
        result = graph.invoke({
            "ingredients": filtered_ingredients,
            "original_ingredients": all_ingredients,
            "difficulty": payload.difficulty,
            "lang": payload.lang,
            "recipe": None,
            "extra_ingredients": [],
            "extra_count": 0,
            "error": None,
            "iteration_count": 0,
            "source_node": None
        })
        
        # Save only newly generated or web-searched recipes (not cache/semantic hits)
        source_node = result.get("source_node", "unknown")
        if result and result.get("recipe"):
            recipe_service = get_recipe_service()
            recipe_service.save_generated_recipe(
                recipe=result["recipe"],
                ingredients=result["ingredients"],
                difficulty=result.get("difficulty", payload.difficulty),
                lang=payload.lang,
                source_node=source_node
            )
        
        if result.get("error"):
            recipe_service = get_recipe_service()
            recipe_service.log_error("ModificationError", result["error"])
            
            return {
                "status": "error",
                "message": result["error"]
            }
        
        return {
            "status": "success",
            "recipe": result.get("recipe", {}),
            "source_node": result.get("source_node", "unknown"),
            "extra_ingredients_added": result.get("extra_ingredients", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in modify_recipe: {e}", exc_info=True)
        recipe_service = get_recipe_service()
        recipe_service.log_error("UnexpectedError", str(e))
        raise HTTPException(
            status_code=500, 
            detail="An internal error occurred while processing the recipe."
        )


@router.post("/feedback")
@limiter.limit("10/minute")
def handle_feedback(payload: FeedbackRequest, request: Request):
    """Cache approved recipes for future use."""
    if not payload.approved:
        return {
            "status": "rejected", 
            "message": i18n.get_message(i18n.FEEDBACK_REJECTED, payload.lang)
        }
    
    try:
        recipe_service = get_recipe_service()
        recipe_service.save_approved_recipe(
            recipe_dict=payload.recipe.dict(),
            ingredients=payload.ingredients,
            difficulty=payload.difficulty,
            lang=payload.lang
        )
        
        return {
            "status": "success", 
            "recipe": payload.recipe.dict(),
            "message": i18n.get_message(i18n.FEEDBACK_SUCCESS, payload.lang)
        }
    except Exception as e:
        logger.error(f"Unexpected error in handle_feedback: {e}", exc_info=True)
        recipe_service = get_recipe_service()
        recipe_service.log_error("FeedbackError", str(e))
        raise HTTPException(
            status_code=500, 
            detail=i18n.get_message(i18n.FEEDBACK_SAVE_FAILED, payload.lang)
        )
