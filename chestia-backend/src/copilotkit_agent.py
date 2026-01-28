"""
CopilotKit Agent Wrapper Module

This module provides CopilotKit-compatible wrapper for the Chestia LangGraph workflow.
It bridges the existing recipe generation agents with CopilotKit's AG-UI protocol.

Architecture:
    Frontend (CopilotKit React) <--> /copilotkit endpoint <--> CopilotKitGraph <--> LangGraph Agents
"""

from typing import TypedDict, List, Optional, Dict, Any, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from agents.recipe_agent import RecipeAgent
from agents.review_agent import ReviewAgent
from agents.search_agent import SearchAgent
import config
import database


class CopilotKitState(TypedDict):
    """
    CopilotKit-compatible state definition.
    
    This state extends the original GraphState with CopilotKit message handling
    to enable bi-directional communication with the frontend.
    
    Attributes:
        messages: CopilotKit message history (required for AG-UI protocol)
        ingredients: Filtered, non-default ingredients from user
        difficulty: Recipe difficulty level ('easy', 'intermediate', 'hard')
        lang: Language preference ('en' or 'tr')
        recipe: Generated recipe object
        extra_ingredients: Additional ingredients suggested during retries
        extra_count: Number of extra ingredients added (max 2)
        error: Error message if any
        iteration_count: Current retry iteration (max 3)
    """
    messages: Annotated[List[BaseMessage], add_messages]
    ingredients: List[str]
    difficulty: str
    lang: str
    recipe: Optional[Dict[str, Any]]
    extra_ingredients: List[str]
    extra_count: int
    error: Optional[str]
    iteration_count: int


def search_cache_node(state: CopilotKitState) -> Dict[str, Any]:
    """
    Check SQLite cache for existing recipes.
    
    This node searches the database for a previously cached recipe
    that matches the current ingredients and difficulty level.
    """
    conn = database.get_db_connection()
    try:
        recipe = database.find_recipe_by_ingredients(
            conn,
            state["ingredients"],
            state["difficulty"]
        )
        if recipe:
            return {
                "recipe": recipe,
                "iteration_count": state.get("iteration_count", 0) + 1,
                "messages": [AIMessage(content=f"Found cached recipe: {recipe.get('name', 'Unknown')}")]
            }
    finally:
        conn.close()
    return {
        "iteration_count": state.get("iteration_count", 0) + 1,
        "messages": [AIMessage(content="No cached recipe found. Generating new recipe...")]
    }


def web_search_node(state: CopilotKitState) -> Dict[str, Any]:
    """
    Search for recipe on web if cache miss.
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
                "iteration_count": state.get("iteration_count", 0) + 1,
                "messages": [AIMessage(content=f"Found recipe via web search: {recipe.get('name', 'Search Result')}")]
            }
    except Exception:
        pass
        
    return {
        "iteration_count": state.get("iteration_count", 0) + 1,
        "messages": [AIMessage(content="Web search yielded no results. Generating new recipe...")]
    }


def generate_recipe_node(state: CopilotKitState) -> Dict[str, Any]:
    """
    Generate a recipe using the RecipeAgent.
    
    Uses Google Gemini via RecipeAgent to create a recipe based on
    the user's ingredients and selected difficulty level.
    """
    agent = RecipeAgent()
    try:
        result = agent.generate(
            state["ingredients"],
            state["difficulty"]
        )
        if "error" in result:
            return {
                "error": result["error"],
                "messages": [AIMessage(content=f"Error generating recipe: {result['error']}")]
            }
        return {
            "recipe": result,
            "iteration_count": state.get("iteration_count", 0) + 1,
            "messages": [AIMessage(content=f"Generated recipe: {result.get('name', 'New Recipe')}")]
        }
    except Exception as e:
        return {
            "error": str(e),
            "messages": [AIMessage(content=f"Failed to generate recipe: {str(e)}")]
        }


def review_recipe_node(state: CopilotKitState) -> Dict[str, Any]:
    """
    Validate the generated recipe using ReviewAgent.
    
    Checks for hallucinations, logical errors, and difficulty matching.
    May suggest additional ingredients if the recipe is invalid.
    """
    from utils import i18n
    
    if state.get("error") or not state.get("recipe"):
        return state

    reviewer = ReviewAgent()
    review = reviewer.validate(
        state["recipe"],
        state["ingredients"],
        state["difficulty"]
    )
    
    if review.get("valid"):
        return {
            "error": None,
            "messages": [AIMessage(content="Recipe validated successfully!")]
        }
    
    # Recipe is invalid - check if we can retry
    current_iteration = state.get("iteration_count", 0)
    current_extra_count = state.get("extra_count", 0)
    lang = state.get("lang", "en")
    
    if current_iteration >= 3:
        return {
            "error": i18n.get_message(i18n.RECIPE_NOT_FOUND, lang),
            "recipe": None,
            "messages": [AIMessage(content=i18n.get_message(i18n.RECIPE_NOT_FOUND, lang))]
        }
    
    suggested = review.get("suggested_extras", [])
    
    if suggested and current_extra_count < 2:
        extras_to_add = suggested[:2 - current_extra_count]
        new_ingredients = state["ingredients"] + extras_to_add
        new_extras = state.get("extra_ingredients", []) + extras_to_add
        
        return {
            "ingredients": new_ingredients,
            "extra_ingredients": new_extras,
            "extra_count": current_extra_count + len(extras_to_add),
            "recipe": None,
            "error": None,
            "messages": [AIMessage(content=f"Adding suggested ingredients: {', '.join(extras_to_add)}")]
        }
    
    if current_iteration < 3:
        return {
            "recipe": None,
            "error": None,
            "messages": [AIMessage(content="Retrying recipe generation...")]
        }
    
    return {
        "error": i18n.get_message(i18n.RECIPE_NOT_FOUND, lang),
        "recipe": None,
        "messages": [AIMessage(content=i18n.get_message(i18n.RECIPE_NOT_FOUND, lang))]
    }


def should_continue(state: CopilotKitState) -> str:
    """
    Router function to determine next step in the workflow.
    
    Returns:
        'end': If recipe is ready or max iterations reached
        'generate': If recipe needs to be generated/regenerated
    """
    if state.get("error"):
        return "end"
    if state.get("recipe"):
        return "end"
    if state.get("iteration_count", 0) >= 3:
        return "end"
    return "generate"


def route_after_cache(state: CopilotKitState) -> str:
    if state.get("recipe"):
        return "end" # Cache hit -> End (skip everything)
    return "web_search"


def route_after_search(state: CopilotKitState) -> str:
    if state.get("recipe"):
        return "review"
    return "generate"



def create_copilotkit_graph() -> StateGraph:
    """
    Create the CopilotKit-compatible LangGraph workflow.
    
    This graph adapts the existing Chestia recipe generation workflow
    to work seamlessly with CopilotKit's AG-UI protocol.
    
    Workflow:
        START -> search_cache -> [has_recipe?] -> END
                                       |
                                       v
                              generate_recipe -> review_recipe -> [valid?] -> END
                                       ^                              |
                                       |______________________________|
                                                (retry with extras)
    
    Returns:
        Compiled StateGraph ready for CopilotKit integration
    """
    workflow = StateGraph(CopilotKitState)
    
    # Add nodes
    workflow.add_node("search_cache", search_cache_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate_recipe", generate_recipe_node)
    workflow.add_node("review_recipe", review_recipe_node)
    
    # Define edges
    workflow.add_edge(START, "search_cache")
    workflow.add_conditional_edges(
        "search_cache",
        route_after_cache,
        {
            "end": END,
            "web_search": "web_search"
        }
    )
    workflow.add_conditional_edges(
        "web_search",
        route_after_search,
        {
            "review": "review_recipe",
            "generate": "generate_recipe"
        }
    )
    workflow.add_edge("generate_recipe", "review_recipe")
    workflow.add_conditional_edges(
        "review_recipe",
        should_continue,
        {
            "end": END,
            "generate": "generate_recipe"
        }
    )
    
    return workflow.compile()


# Pre-compiled graph instance for CopilotKit endpoint
copilotkit_graph = create_copilotkit_graph()


def get_initial_state(
    ingredients: List[str],
    difficulty: str,
    lang: str = "en",
    message: Optional[str] = None
) -> CopilotKitState:
    """
    Create initial state for CopilotKit workflow invocation.
    
    Args:
        ingredients: User's ingredient list (will be filtered)
        difficulty: Recipe difficulty level
        lang: Language preference ('en' or 'tr')
        message: Optional initial user message
    
    Returns:
        CopilotKitState ready for graph invocation
    """
    # Filter default ingredients
    filtered = config.filter_default_ingredients(ingredients)
    
    initial_message = message or f"Generate a {difficulty} recipe with: {', '.join(filtered)}"
    
    return CopilotKitState(
        messages=[HumanMessage(content=initial_message)],
        ingredients=filtered,
        difficulty=difficulty,
        lang=lang,
        recipe=None,
        extra_ingredients=[],
        extra_count=0,
        error=None,
        iteration_count=0
    )
