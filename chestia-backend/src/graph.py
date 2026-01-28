from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from agents.recipe_agent import RecipeAgent
from agents.review_agent import ReviewAgent
from agents.search_agent import SearchAgent
from database import get_db_connection, find_recipe_by_ingredients
from utils import i18n

class GraphState(TypedDict):
    ingredients: List[str]              # Filtered, non-default ingredients
    original_ingredients: List[str]     # User's original input (for reference)
    difficulty: str                     # 'easy', 'intermediate', or 'hard'
    lang: str                           # 'en' or 'tr'
    recipe: Optional[Dict[str, Any]]    # Generated recipe
    extra_ingredients: List[str]        # Track what extras were added
    extra_count: int                    # How many extras added (max 2)
    error: Optional[str]                # Error message if any
    iteration_count: int                # Current iteration (max 3)


def search_cache_node(state: GraphState):
    """Check if a recipe for these ingredients + difficulty exists in SQLite"""
    conn = get_db_connection()
    try:
        recipe = find_recipe_by_ingredients(
            conn,
            state["ingredients"],
            state["difficulty"]
        )
        if recipe:
            return {"recipe": recipe, "iteration_count": state.get("iteration_count", 0) + 1}
    finally:
        conn.close()
    return {"iteration_count": state.get("iteration_count", 0) + 1}


def web_search_node(state: GraphState):
    """
    Search for recipe on web if cache miss.
    
    If successful, returns recipe and skips generation.
    If fails/empty, proceeds to generation with no recipe.
    """
    try:
        agent = SearchAgent()
        recipe = agent.search(
            state["ingredients"],
            state["difficulty"]
        )
        if recipe:
            return {
                "recipe": recipe, 
                "iteration_count": state.get("iteration_count", 0) + 1
            }
    except Exception:
        # Fallback to generation on any error
        pass
        
    return {"iteration_count": state.get("iteration_count", 0) + 1}


def generate_recipe_node(state: GraphState):
    """Generate a recipe using LLM with STRICT ingredient constraints"""
    agent = RecipeAgent()
    try:
        result = agent.generate(
            state["ingredients"],
            state["difficulty"]
        )
        if "error" in result:
            return {"error": result["error"]}
        return {
            "recipe": result, 
            "iteration_count": state.get("iteration_count", 0) + 1
        }
    except Exception as e:
        return {"error": str(e)}


def review_recipe_node(state: GraphState):
    """
    Validate recipe and handle auto-retry with extra ingredients.
        
    Logic:
    1. If valid -> proceed to END
    2. If invalid and has suggestions and extra_count < 2 and iteration < 3:
       -> Add suggested extras and retry
    3. Otherwise -> Return error
    
    """
    if state.get("error") or not state.get("recipe"):
        return state

    reviewer = ReviewAgent()
    review = reviewer.validate(
        state["recipe"],
        state["ingredients"],
        state["difficulty"]
    )
    
    if review.get("valid"):
        # Recipe is valid, no changes needed
        return {"error": None}
    
    # Recipe is invalid - check if we can retry
    current_iteration = state.get("iteration_count", 0)
    current_extra_count = state.get("extra_count", 0)
    lang = state.get("lang", "en")
    
    # Check limits
    if current_iteration >= 3:
        return {
            "error": i18n.get_message(i18n.RECIPE_NOT_FOUND, lang),
            "recipe": None
        }
    
    # Try to get suggested extras from review
    suggested = review.get("suggested_extras", [])
    
    if suggested and current_extra_count < 2:
        # Add up to 2 extras total
        extras_to_add = suggested[:2 - current_extra_count]
        new_ingredients = state["ingredients"] + extras_to_add
        new_extras = state.get("extra_ingredients", []) + extras_to_add
        
        return {
            "ingredients": new_ingredients,
            "extra_ingredients": new_extras,
            "extra_count": current_extra_count + len(extras_to_add),
            "recipe": None,  # Clear recipe to trigger regeneration
            "error": None
        }
    
    # No suggestions or max extras reached, but still have iterations
    if current_iteration < 3:
        return {
            "recipe": None,  # Clear to retry
            "error": None
        }
    
    # All retries exhausted
    return {
        "error": i18n.get_message(i18n.RECIPE_NOT_FOUND, lang),
        "recipe": None
    }


def route_after_review(state: GraphState):
    """Route based on review outcome"""
    # If there's an error, we're done
    if state.get("error"):
        return END
    
    # If no recipe (was cleared for retry), go back to generate
    if not state.get("recipe"):
        # Check iteration limit
        if state.get("iteration_count", 0) >= 3:
            return END
        return "generate"
    
    # Valid recipe exists, we're done
    return END


def route_after_cache(state: GraphState):
    """Route after cache check"""
    if state.get("recipe"):
        return "review_recipe" # Cache hit -> Review
    return "web_search"     # Cache miss -> Web Search


def route_after_search(state: GraphState):
    """Route after web search"""
    if state.get("recipe"):
        return "review_recipe" # Search hit -> Review
    return "generate_recipe" # Search miss -> Generate


def create_graph():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("search_cache", search_cache_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate_recipe", generate_recipe_node)
    workflow.add_node("review_recipe", review_recipe_node)
    
    workflow.add_edge(START, "search_cache")
    
    workflow.add_conditional_edges(
        "search_cache",
        route_after_cache,
        {
            "review_recipe": "review_recipe",
            "web_search": "web_search"
        }
    )
    
    workflow.add_conditional_edges(
        "web_search",
        route_after_search,
        {
            "review_recipe": "review_recipe",
            "generate_recipe": "generate_recipe"
        }
    )
    
    workflow.add_edge("generate_recipe", "review_recipe")
    
    workflow.add_conditional_edges(
        "review_recipe",
        route_after_review,
        {
            "generate": "generate_recipe",
            END: END
        }
    )
    
    return workflow.compile()
