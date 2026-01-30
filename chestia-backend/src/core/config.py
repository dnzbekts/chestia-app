"""
Configuration settings for Chestia backend.

Contains only configuration constants and dictionaries.
Domain logic for ingredients is in domain/ingredients.py.
"""

# CopilotKit Configuration
COPILOTKIT_AGENT_NAME = "chestia_recipe_agent"
COPILOTKIT_AGENT_DESCRIPTION = "Intelligent recipe generation from user-provided ingredients with auto-retry and validation"

# LLM Configuration
LLM_CONFIG = {
    "default_model": "gemini-2.0-flash",
    "recipe_temperature": 0.7,
    "review_temperature": 0.0,
    "search_temperature": 0.1,
}

# Search Configuration
SEARCH_CONFIG = {
    "max_results": 3,
    "search_depth": "advanced",
}

# Graph Configuration
GRAPH_CONFIG = {
    "max_iterations": 3,
    "max_extra_ingredients": 2,
    "semantic_search_threshold": 0.65,  # Balanced threshold for precision/recall
}

# Database Configuration
DB_CONFIG = {
    "embedding_model": "models/gemini-embedding-001",
    "embedding_dimensions": 3072,
}
