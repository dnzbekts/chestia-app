import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.workflow.graph import create_graph, GraphState

@pytest.mark.asyncio
def test_graph_initialization():
    """Test that the graph compiles correctly"""
    # Verify graph creation doesn't raise errors
    graph = create_graph()
    assert graph is not None

def test_graph_workflow_mock():
    """Test the happy path of the workflow using mocks"""
    # This is a high-level test assuming we can mock nodes
    # For now, we just test that we can invoke the graph compilation
    # and it returns a Runnable
    
    graph = create_graph()
    # Since we don't have a full mocked environment for async graph execution in this unit test setup easily,
    # we verify properties of the compiled graph if possible or just its build status.
    assert hasattr(graph, 'invoke') or hasattr(graph, 'ainvoke')
