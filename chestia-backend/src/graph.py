from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from agents.recipe_agent import RecipeAgent
from agents.review_agent import ReviewAgent
from database import get_db_connection, find_recipe_by_ingredients

class GraphState(TypedDict):
    ingredients: List[str]
    difficulty: str  # 'easy', 'intermediate', or 'hard'
    recipe: Optional[Dict[str, Any]]
    needs_approval: bool
    extra_ingredients: List[str]
    error: Optional[str]
    iteration_count: int

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

def generate_recipe_node(state: GraphState):
    """Generate a recipe using LLM, respecting difficulty level"""
    agent = RecipeAgent()
    try:
        # Use existing ingredients list and difficulty
        result = agent.generate(
            state["ingredients"],
            state["difficulty"]
        )
        if "error" in result:
             return {"error": result["error"]}
        return {"recipe": result, "iteration_count": state.get("iteration_count", 0) + 1}
    except Exception as e:
        return {"error": str(e)}

def review_recipe_node(state: GraphState):
    """Validate the generated recipe for hallucinations and difficulty match"""
    if state.get("error") or not state.get("recipe"):
        return state

    reviewer = ReviewAgent()
    review = reviewer.validate(
        state["recipe"],
        state["ingredients"],
        state["difficulty"]
    )
    
    if not review["valid"]:
        # Check if it's because of extra ingredients
        reason = review["reasoning"].lower()
        if "extra" in reason or "additional" in reason:
            # Extract suggested ingredients (simplified)
            return {
                "needs_approval": True,
                "error": review["reasoning"],
                "iteration_count": state.get("iteration_count", 0) + 1
            }
        else:
            # Complete hallucination or invalid recipe
            return {
                "error": review["reasoning"],
                "iteration_count": state.get("iteration_count", 0) + 1
            }
    
    return {"iteration_count": state.get("iteration_count", 0) + 1}

def should_generate(state: GraphState):
    """Condition to check if we need to generate or we have a cache hit"""
    if state.get("recipe"):
        return "review"
    return "generate"

def route_after_review(state: GraphState):
    """Route based on review outcome"""
    if state.get("needs_approval"):
        return END
    if not state.get("recipe"):
        # If recipe was cleared due to logic error, retry unless we hit max
        if state.get("iteration_count", 0) >= 3:
            return END
        return "generate"
    return END

def create_graph():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("search_cache", search_cache_node)
    workflow.add_node("generate_recipe", generate_recipe_node)
    workflow.add_node("review_recipe", review_recipe_node)
    
    workflow.add_edge(START, "search_cache")
    
    workflow.add_conditional_edges(
        "search_cache",
        should_generate,
        {
            "generate": "generate_recipe",
            "review": "review_recipe"
        }
    )
    
    workflow.add_edge("generate_recipe", "review_recipe")
    
    workflow.add_conditional_edges(
        "review_recipe",
        route_after_review,
        {
            "generate": "generate_recipe",
            "end": END
        }
    )
    
    return workflow.compile()
