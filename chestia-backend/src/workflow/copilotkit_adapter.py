"""
CopilotKit adapter for Chestia recipe generation.

Simplified to use the main graph from graph.py, acting as a thin adapter.
"""

from src.workflow.graph import RecipeGraphOrchestrator

# Create a dedicated orchestrator instance for CopilotKit with memory persistence
_copilotkit_orchestrator = RecipeGraphOrchestrator()

# Export compiled graph with checkpointer for CopilotKit integration
copilotkit_graph = _copilotkit_orchestrator.create_graph(with_checkpointer=True)
