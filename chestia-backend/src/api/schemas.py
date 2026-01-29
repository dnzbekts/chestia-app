"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Literal
import re


class GenerateRequest(BaseModel):
    """Request to generate a new recipe from ingredients."""
    ingredients: List[str] = Field(..., min_length=3, max_length=20)
    difficulty: Literal["easy", "intermediate", "hard"] = Field(
        ...,
        description="Recipe difficulty level: easy, intermediate, or hard"
    )
    lang: Literal["tr", "en"] = Field("en", description="Preferred language for messages: tr or en")

    @validator('ingredients', each_item=True)
    def validate_ingredient_chars(cls, v):
        if not re.match(r"^[a-zA-Z0-9\s,\-çÇğĞıİöÖşŞüÜ]+$", v):
            raise ValueError("Ingredient contains invalid characters")
        if len(v) > 50:
            raise ValueError("Ingredient name too long")
        return v


class ModifyRequest(BaseModel):
    """Request to modify/regenerate a recipe."""
    original_ingredients: List[str] = Field(..., min_length=3, max_length=20)
    new_ingredients: Optional[List[str]] = Field(None, max_length=20)
    difficulty: Literal["easy", "intermediate", "hard"]
    modification_note: Optional[str] = None  # e.g., "make it spicier"
    lang: Literal["tr", "en"] = Field("en", description="Preferred language for messages")
    
    @validator('original_ingredients', 'new_ingredients', each_item=True)
    def validate_ingredient_chars(cls, v):
        if v is None:
            return v
        if not re.match(r"^[a-zA-Z0-9\s,\-çÇğĞıİöÖşŞüÜ]+$", v):
            raise ValueError("Ingredient contains invalid characters")
        if len(v) > 50:
            raise ValueError("Ingredient name too long")
        return v


class RecipeSchema(BaseModel):
    """Structured schema for a recipe."""
    name: str = Field(..., min_length=1, max_length=100)
    ingredients: List[str] = Field(..., min_length=1, max_length=50)
    steps: List[str] = Field(..., min_length=1, max_length=100)
    metadata: Optional[Dict[str, Any]] = Field(None)

    @validator('ingredients', 'steps', each_item=True)
    def validate_content_chars(cls, v):
        if len(v) > 200:
            raise ValueError("Item content too long")
        return v


class FeedbackRequest(BaseModel):
    """Request to provide feedback on a generated recipe."""
    ingredients: List[str] = Field(..., min_length=1, max_length=20)
    difficulty: Literal["easy", "intermediate", "hard"]
    approved: bool
    recipe: RecipeSchema
    lang: Literal["tr", "en"] = Field("en")
