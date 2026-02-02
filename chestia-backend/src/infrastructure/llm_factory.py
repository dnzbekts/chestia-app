"""
LLM Factory - Centralized LLM initialization following Single Responsibility Principle.

This factory eliminates duplicate LLM initialization code across agents and provides
a single source of truth for LLM configuration.
"""

import os
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


class LLMFactory:
    """Factory for creating and configuring LLM instances."""
    
    @staticmethod
    def _validate_api_key(api_key: Optional[str]) -> str:
        """
        Validate Google API key.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            Validated API key
            
        Raises:
            RuntimeError: If API key is missing or invalid
        """
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is not set in environment variables. "
                "Please set it in your .env file or environment."
            )
        
        # Check for placeholder values
        placeholder_values = ["YOUR_KEY_HERE", "your-api-key", "REPLACE_ME"]
        if api_key.strip() in placeholder_values:
            raise RuntimeError(
                f"GOOGLE_API_KEY contains a placeholder value: '{api_key}'. "
                "Please replace it with a valid API key."
            )
        
        # Basic format validation (Google API keys typically start with 'AIza')
        if not api_key.startswith("AIza") or len(api_key) < 20:
            raise RuntimeError(
                "GOOGLE_API_KEY appears to be invalid. "
                "Google API keys typically start with 'AIza' and are at least 20 characters long."
            )
        
        return api_key
    
    @staticmethod
    def create_llm(
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        api_key: Optional[str] = None
    ) -> ChatGoogleGenerativeAI:
        """
        Create a configured LLM instance.
        
        Args:
            model: Model name (default: gemini-2.0-flash)
            temperature: Sampling temperature (default: 0.7)
            api_key: Optional API key override (uses env var if not provided)
            
        Returns:
            Configured ChatGoogleGenerativeAI instance
            
        Raises:
            RuntimeError: If API key validation fails
        """
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
        
        validated_key = LLMFactory._validate_api_key(api_key)
        
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=validated_key,
            temperature=temperature
        )
    
    @staticmethod
    def create_recipe_llm() -> ChatGoogleGenerativeAI:
        """
        Create LLM optimized for recipe generation.
        
        Returns:
            LLM instance with creative temperature (0.7)
        """
        return LLMFactory.create_llm(
            model="gemini-2.0-flash",
            temperature=0.7
        )
    
    @staticmethod
    def create_review_llm() -> ChatGoogleGenerativeAI:
        """
        Create LLM optimized for recipe validation and review.
        
        Returns:
            LLM instance with deterministic temperature (0)
        """
        return LLMFactory.create_llm(
            model="gemini-2.0-flash",
            temperature=0
        )
    
    @staticmethod
    def create_search_llm() -> ChatGoogleGenerativeAI:
        """
        Create LLM optimized for parsing search results.
        
        Returns:
            LLM instance with low temperature (0.1) for accurate parsing
        """
        return LLMFactory.create_llm(
            model="gemini-2.0-flash",
            temperature=0.1
        )

    @staticmethod
    def create_validation_llm() -> ChatGoogleGenerativeAI:
        """
        Create LLM optimized for ingredient validation.
        
        Returns:
            LLM instance with low temperature (0.1) for accurate ingredient validation
        """
        return LLMFactory.create_llm(
            model="gemini-2.0-flash",
            temperature=0.1
        )
