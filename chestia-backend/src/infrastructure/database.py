"""
Database operations for Chestia backend.

Refactored with context manager for connection management,
embedding service abstraction, and improved error handling.
"""

import sqlite3
import os
import json
import sqlite_vec
import logging
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from src.core.config import DB_CONFIG
from src.core.exceptions import DatabaseError, EmbeddingGenerationError

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings with error handling and caching."""
    
    def __init__(self):
        """Initialize the embedding service."""
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=DB_CONFIG["embedding_model"]
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using Gemini.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector
            
        Raises:
            EmbeddingGenerationError: If embedding generation fails
        """
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}", exc_info=True)
            raise EmbeddingGenerationError(
                f"Failed to generate embedding: {str(e)}",
                details={"text_length": len(text)}
            )


# Global embedding service instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the global embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


@contextmanager
def get_db_connection(db_path: Optional[str] = None):
    """
    Context manager for database connections.
    
    Ensures proper connection cleanup and transaction management.
    
    Args:
        db_path: Optional path to database file
        
    Yields:
        SQLite connection
        
    Example:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # ... perform operations
    """
    initdb = False
    
    if db_path is None:
        db_path = os.path.join(os.path.dirname(__file__), 'chestia.db')
        initdb = True
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Load sqlite-vec extension
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        
        if initdb:
            init_db(conn)
        
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        raise DatabaseError(f"Database operation failed: {str(e)}")
    finally:
        if conn:
            conn.close()


def init_db(conn):
    """
    Initialize database schema.
    
    Args:
        conn: Database connection
    """
    cursor = conn.cursor()
    
    # Create recipes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ingredients JSON NOT NULL,
            difficulty TEXT NOT NULL,
            lang TEXT NOT NULL DEFAULT 'en',
            steps JSON NOT NULL,
            metadata JSON
        )
    """)
    
    # Create logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            error_type TEXT,
            message TEXT,
            request_id TEXT
        )
    """)
    
    # Create vector table for semantic search
    # Using configured dimensions for embeddings
    embedding_dims = DB_CONFIG["embedding_dimensions"]
    cursor.execute(f"""
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_recipes USING vec0(
            recipe_id INTEGER PRIMARY KEY,
            embedding float[{embedding_dims}]
        )
    """)
    
    # Migration: Add lang column if it doesn't exist
    try:
        cursor.execute("SELECT lang FROM recipes LIMIT 1")
    except sqlite3.OperationalError:
        logger.info("Migrating database: adding 'lang' column to 'recipes' table")
        cursor.execute("ALTER TABLE recipes ADD COLUMN lang TEXT NOT NULL DEFAULT 'en'")
    
    conn.commit()
    logger.info("Database schema initialized successfully")


def find_recipe_by_ingredients(
    conn, 
    ingredients: List[str], 
    difficulty: str,
    lang: str = "en"
) -> Optional[Dict[str, Any]]:
    """
    Find a recipe matching non-default ingredients AND difficulty level.
    
    Default ingredients (water, salt, oil, spices, etc.) are filtered out
    before lookup to optimize cache hits. Difficulty is part of cache key.
    
    This means:
    - ["pasta", "tomato", "salt"], "easy" → Different from "hard"
    - ["pasta", "tomato"], "easy" with defaults → Same cache as without defaults
    
    Args:
        conn: Database connection
        ingredients: List of ingredient names (may include defaults)
        difficulty: Recipe difficulty level ('easy', 'intermediate', 'hard')
        
    Returns:
        Recipe dict if found, None otherwise
    """
    from src.domain.ingredients import filter_default_ingredients
    
    cursor = conn.cursor()
    # Filter out default ingredients and sort for consistent lookup
    non_default_ingredients = filter_default_ingredients(ingredients)
    ingredients_json = json.dumps(sorted(non_default_ingredients))
    
    logger.info(f"Cache lookup: {ingredients_json}, difficulty={difficulty}, lang={lang}")
    
    cursor.execute("""
        SELECT * FROM recipes WHERE ingredients = ? AND difficulty = ? AND lang = ?
    """, (ingredients_json, difficulty, lang))
    
    row = cursor.fetchone()
    if row:
        logger.info(f"Cache HIT: recipe_id={row['id']}, name={row['name']}")
        return dict(row)
    
    logger.info(f"Cache MISS for: {ingredients_json}")
    return None


def log_error(
    conn, 
    error_type: str, 
    message: str, 
    request_id: Optional[str] = None
) -> None:
    """
    Log an error to the logs table.
    
    Args:
        conn: Database connection
        error_type: Type of error
        message: Error message
        request_id: Optional request identifier
    """
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (error_type, message, request_id)
        VALUES (?, ?, ?)
    """, (error_type, message, request_id))
    conn.commit()
    logger.info(f"Logged error: {error_type} - {message[:100]}")


def find_recipe_semantically(
    conn, 
    ingredients: List[str], 
    difficulty: str, 
    lang: str = "en",
    threshold: Optional[float] = None
) -> Optional[Dict[str, Any]]:
    """
    Find a recipe using semantic similarity on ingredients.
    
    Args:
        conn: Database connection
        ingredients: List of ingredients
        difficulty: Recipe difficulty level
        threshold: Optional similarity threshold (uses config default if None)
        
    Returns:
        Recipe dict if found, None otherwise
    """
    from src.core.config import GRAPH_CONFIG
    
    if threshold is None:
        threshold = GRAPH_CONFIG["semantic_search_threshold"]
    
    try:
        query_text = f"Ingredients: {', '.join(sorted(ingredients))}"
        embedding_service = get_embedding_service()
        query_vector = embedding_service.generate_embedding(query_text)
        
        cursor = conn.cursor()
        
        # Check if any embeddings exist
        cursor.execute("SELECT COUNT(*) as cnt FROM vec_recipes")
        count = cursor.fetchone()['cnt']
        logger.info(f"Semantic search: {count} embeddings in database")
        
        if count == 0:
            logger.warning("No embeddings in database - semantic search will fail")
            return None
        
        cursor.execute("""
            SELECT 
                r.*, 
                v.distance
            FROM vec_recipes v
            JOIN recipes r ON v.recipe_id = r.id
            WHERE v.embedding MATCH ? AND r.difficulty = ? AND r.lang = ? AND k = 1
            ORDER BY v.distance
        """, (sqlite_vec.serialize_float32(query_vector), difficulty, lang))
        
        row = cursor.fetchone()
        if row and row['distance'] < threshold:
            logger.info(f"Semantic match found with distance: {row['distance']}")
            return dict(row)
        
        logger.debug(f"No semantic match within threshold {threshold}")
        return None
        
    except EmbeddingGenerationError:
        logger.warning("Semantic search skipped due to embedding error")
        return None
    except Exception as e:
        logger.error(f"Semantic search failed: {e}", exc_info=True)
        return None


def save_recipe(
    conn, 
    name: str, 
    ingredients: List[str], 
    difficulty: str, 
    lang: str,
    steps: List[str], 
    metadata: Optional[Dict[str, Any]] = None
) -> int:
    """
    Save a recipe and its embedding to the database.
    
    Checks for duplicates before saving. If a recipe with the same
    ingredients and difficulty already exists, returns the existing ID.
    
    Args:
        conn: Database connection
        name: Recipe name
        ingredients: List of ingredients
        difficulty: Recipe difficulty level
        steps: List of cooking steps
        metadata: Optional recipe metadata
        
    Returns:
        Recipe ID (existing if duplicate, new if created)
        
    Raises:
        DatabaseError: If save operation fails
    """
    # Check for existing recipe with same ingredients, difficulty and language
    existing = find_recipe_by_ingredients(conn, ingredients, difficulty, lang)
    if existing:
        logger.info(
            f"Recipe already exists with ID {existing['id']}, "
            f"skipping duplicate for '{name}'"
        )
        return existing['id']
    
    cursor = conn.cursor()
    
    try:
        # 1. Save to relational table
        cursor.execute("""
            INSERT INTO recipes (name, ingredients, difficulty, lang, steps, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            json.dumps(sorted(ingredients)),
            difficulty,
            lang,
            json.dumps(steps),
            json.dumps(metadata or {})
        ))
        recipe_id = cursor.lastrowid
        
        # 2. Generate and save embedding (with error handling)
        try:
            embedding_text = f"Ingredients: {', '.join(sorted(ingredients))}"
            embedding_service = get_embedding_service()
            embedding = embedding_service.generate_embedding(embedding_text)
            
            cursor.execute("""
                INSERT INTO vec_recipes (recipe_id, embedding)
                VALUES (?, ?)
            """, (recipe_id, sqlite_vec.serialize_float32(embedding)))
            
        except EmbeddingGenerationError as e:
            logger.warning(
                f"Failed to generate embedding for recipe {recipe_id}, "
                f"semantic search will not work for this recipe: {e}"
            )
            # Continue anyway - recipe is still saved, just without embedding
        
        conn.commit()
        logger.info(f"Saved recipe '{name}' with ID {recipe_id}")
        return recipe_id
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to save recipe '{name}': {e}", exc_info=True)
        raise DatabaseError(
            f"Failed to save recipe: {str(e)}",
            details={"recipe_name": name}
        )
