"""
LangGraph workflow for recipe generation.

Refactored with LangGraph best practices: dependency injection,
checkpointer support, proper error handling, and configuration management.
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
import logging
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.workflow.agents.recipe_agent import RecipeAgent
from src.workflow.agents.review_agent import ReviewAgent
from src.workflow.agents.search_agent import SearchAgent
from src.infrastructure.database import get_db_connection, find_recipe_by_ingredients, find_recipe_semantically
from src.infrastructure.localization import i18n
from src.core.config import GRAPH_CONFIG
from src.core.exceptions import RecipeGenerationError

logger = logging.getLogger(__name__)


# State reducer for lists - appends new items
def add_extras(existing: List[str], new: List[str]) -> List[str]:
    """Reducer for extra_ingredients list."""
    return existing + new


class GraphState(TypedDict):
    """State for the recipe generation workflow."""
    ingredients: List[str]              # Filtered, non-default ingredients
    original_ingredients: List[str]     # User's original input (for reference)
    difficulty: str                     # 'easy', 'intermediate', or 'hard'
    lang: str                           # 'en' or 'tr'
    recipe: Optional[Dict[str, Any]]    # Generated recipe
    extra_ingredients: Annotated[List[str], add_extras]  # Track what extras were added
    extra_count: int                    # How many extras added
    error: Optional[str]                # Error message if any
    iteration_count: int                # Current iteration


class RecipeGraphOrchestrator:
    """Orchestrator for the recipe generation graph with dependency injection."""
    
    def __init__(
        self,
        recipe_agent: Optional[RecipeAgent] = None,
        review_agent: Optional[ReviewAgent] = None,
        search_agent: Optional[SearchAgent] = None
    ):
        """
        Initialize the orchestrator.
        
        Args:
            recipe_agent: Optional RecipeAgent instance (creates new if None)
            review_agent: Optional ReviewAgent instance (creates new if None)
            search_agent: Optional SearchAgent instance (creates new if None)
        """
        self.recipe_agent = recipe_agent or RecipeAgent()
        self.review_agent = review_agent or ReviewAgent()
        self.search_agent = search_agent or SearchAgent()
        
        # Load configuration
        self.max_iterations = GRAPH_CONFIG["max_iterations"]
        self.max_extras = GRAPH_CONFIG["max_extra_ingredients"]

    def search_cache_node(self, state: GraphState) -> Dict[str, Any]:
        """Check if a recipe for these ingredients + difficulty exists in SQLite."""
        with get_db_connection() as conn:
            recipe = find_recipe_by_ingredients(
                conn,
                state["ingredients"],
                state["difficulty"]
            )
            if recipe:
                logger.info("Cache hit - recipe found")
                return {
                    "recipe": recipe,
                    "iteration_count": state.get("iteration_count", 0) + 1,
                    "messages": [i18n.get_message(i18n.SEARCHING_CACHE, state.get("lang", "en"))]
                }
        
        logger.debug("Cache miss - no exact match")
        return {
            "iteration_count": state.get("iteration_count", 0) + 1,
            "messages": [i18n.get_message(i18n.SEARCHING_CACHE, state.get("lang", "en"))]
        }

    def semantic_search_node(self, state: GraphState) -> Dict[str, Any]:
        """
        Check if a similar recipe exists using semantic embeddings.
        Fills the gap between exact cache and web search.
        """
        try:
            with get_db_connection() as conn:
                recipe = find_recipe_semantically(
                    conn,
                    state["ingredients"],
                    state["difficulty"]
                )
                if recipe:
                    logger.info("Semantic search hit - similar recipe found")
                    return {
                        "recipe": recipe,
                        "messages": [i18n.get_message(i18n.SEMANTIC_SEARCH_HIT, state.get("lang", "en"))]
                    }
        except Exception as e:
            # Silently fail and fallback to web search
            logger.warning(f"Semantic search failed: {e}")
        
        logger.debug("Semantic search miss")
        return {"messages": [i18n.get_message(i18n.SEMANTIC_SEARCH_MISS, state.get("lang", "en"))]}

    def web_search_node(self, state: GraphState) -> Dict[str, Any]:
        """
        Search for recipe on web if cache miss.
        
        If successful, returns recipe and skips generation.
        If fails/empty, proceeds to generation with no recipe.
        """
        try:
            recipe = self.search_agent.search(
                state["ingredients"],
                state["difficulty"]
            )
            if recipe:
                logger.info("Web search hit - recipe found")
                return {
                    "recipe": recipe,
                    "messages": [i18n.get_message(i18n.WEB_SEARCH_HIT, state.get("lang", "en"))]
                }
        except Exception as e:
            logger.warning(f"Web search failed: {e}")
        
        logger.debug("Web search miss - will generate new recipe")
        return {"messages": [i18n.get_message(i18n.WEB_SEARCH_MISS, state.get("lang", "en"))]}

    def generate_recipe_node(self, state: GraphState) -> Dict[str, Any]:
        """Generate a recipe using LLM with STRICT ingredient constraints."""
        try:
            result = self.recipe_agent.generate(
                state["ingredients"],
                state["difficulty"]
            )
            logger.info(f"Generated recipe: {result.get('name', 'Unknown')}")
            return {
                "recipe": result,
                "messages": [i18n.get_message(i18n.GENERATING_RECIPE, state.get("lang", "en"))]
            }
        except RecipeGenerationError as e:
            logger.error(f"Recipe generation failed: {e}")
            return {
                "error": str(e),
                "messages": [i18n.get_message(i18n.GENERATION_ERROR, state.get("lang", "en"))]
            }
        except Exception as e:
            logger.error(f"Unexpected error in recipe generation: {e}", exc_info=True)
            return {
                "error": f"Recipe generation failed: {str(e)}",
                "messages": [i18n.get_message(i18n.GENERATION_ERROR, state.get("lang", "en"))]
            }

    def review_recipe_node(self, state: GraphState) -> Dict[str, Any]:
        """
        Validate recipe and handle auto-retry with extra ingredients.
            
        Logic:
        1. If valid -> proceed to END
        2. If invalid and has suggestions and limits not exceeded:
           -> Add suggested extras and retry
        3. Otherwise -> Return error
        """
        if state.get("error") or not state.get("recipe"):
            return state

        try:
            review = self.review_agent.validate(
                state["recipe"],
                state["ingredients"],
                state["difficulty"]
            )
        except Exception as e:
            logger.error(f"Review failed: {e}", exc_info=True)
            return {"error": f"Recipe review failed: {str(e)}"}
        
        if review.get("valid"):
            logger.info("Recipe validated successfully")
            return {
                "error": None,
                "messages": [i18n.get_message(i18n.RECIPE_VALIDATED, state.get("lang", "en"))]
            }
        
        # Recipe is invalid - check if we can retry
        current_iteration = state.get("iteration_count", 0)
        current_extra_count = state.get("extra_count", 0)
        lang = state.get("lang", "en")
        
        logger.info(
            f"Recipe invalid - iteration {current_iteration}/{self.max_iterations}, "
            f"extras {current_extra_count}/{self.max_extras}"
        )
        
        # Check iteration limit
        if current_iteration >= self.max_iterations:
            logger.warning("Max iterations reached")
            return {
                "error": i18n.get_message(i18n.RECIPE_NOT_FOUND, lang),
                "recipe": None
            }
        
        # Try to get suggested extras from review
        suggested = review.get("suggested_extras", [])
        
        if suggested and current_extra_count < self.max_extras:
            # Add up to max_extras total
            extras_to_add = suggested[:self.max_extras - current_extra_count]
            new_ingredients = state["ingredients"] + extras_to_add
            new_extras = state.get("extra_ingredients", []) + extras_to_add
            
            logger.info(f"Adding extra ingredients: {extras_to_add}")
            return {
                "ingredients": new_ingredients,
                "extra_ingredients": new_extras,
                "extra_count": current_extra_count + len(extras_to_add),
                "recipe": None,  # Clear recipe to trigger regeneration
                "error": None
            }
        
        # No suggestions or max extras reached, but still have iterations
        if current_iteration < self.max_iterations:
            logger.info("Retrying without adding extras")
            return {
                "recipe": None,  # Clear to retry
                "error": None
            }
        
        # All retries exhausted
        logger.warning("All retry attempts exhausted")
        return {
            "error": i18n.get_message(i18n.RECIPE_NOT_FOUND, lang),
            "recipe": None
        }

    def route_after_review(self, state: GraphState) -> str:
        """Route based on review outcome."""
        if state.get("error"):
            return END
        
        if not state.get("recipe"):
            if state.get("iteration_count", 0) >= self.max_iterations:
                return END
            return "generate"
        
        return END

    def route_after_cache(self, state: GraphState) -> str:
        """Route after cache check."""
        if state.get("recipe"):
            return "review_recipe"
        return "semantic_search"

    def route_after_semantic(self, state: GraphState) -> str:
        """Route after semantic search."""
        if state.get("recipe"):
            return "review_recipe"
        return "web_search"

    def route_after_search(self, state: GraphState) -> str:
        """Route after web search."""
        if state.get("recipe"):
            return "review_recipe"
        return "generate_recipe"

    def create_graph(self, with_checkpointer: bool = False):
        """
        Create the recipe generation workflow graph.
        
        Args:
            with_checkpointer: If True, adds MemorySaver checkpointer for state persistence
            
        Returns:
            Compiled StateGraph
        """
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("search_cache", self.search_cache_node)
        workflow.add_node("semantic_search", self.semantic_search_node)
        workflow.add_node("web_search", self.web_search_node)
        workflow.add_node("generate_recipe", self.generate_recipe_node)
        workflow.add_node("review_recipe", self.review_recipe_node)
        
        # Add edges
        workflow.add_edge(START, "search_cache")
        
        workflow.add_conditional_edges(
            "search_cache",
            self.route_after_cache,
            {
                "review_recipe": "review_recipe",
                "semantic_search": "semantic_search"
            }
        )
        
        workflow.add_conditional_edges(
            "semantic_search",
            self.route_after_semantic,
            {
                "review_recipe": "review_recipe",
                "web_search": "web_search"
            }
        )
        
        workflow.add_conditional_edges(
            "web_search",
            self.route_after_search,
            {
                "review_recipe": "review_recipe",
                "generate_recipe": "generate_recipe"
            }
        )
        
        workflow.add_edge("generate_recipe", "review_recipe")
        
        workflow.add_conditional_edges(
            "review_recipe",
            self.route_after_review,
            {
                "generate": "generate_recipe",
                END: END
            }
        )
        
        # Compile with optional checkpointer
        if with_checkpointer:
            checkpointer = MemorySaver()
            logger.info("Graph compiled with MemorySaver checkpointer")
            return workflow.compile(checkpointer=checkpointer)
        
        logger.info("Graph compiled without checkpointer")
        return workflow.compile()


# For backward compatibility - create default instance
def create_graph():
    """Create default recipe generation graph."""
    orchestrator = RecipeGraphOrchestrator()
    return orchestrator.create_graph(with_checkpointer=False)
