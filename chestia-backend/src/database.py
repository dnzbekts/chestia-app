import sqlite3
import os
import json
import sqlite_vec
from typing import List, Dict, Any, Optional

def get_db_connection(db_path=None):
    if db_path is None:
        # Default to a file in the same directory
        db_path = os.path.join(os.path.dirname(__file__), 'chestia.db')
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Load sqlite-vec extension
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    
    return conn

def generate_embedding(text: str) -> List[float]:
    """Generate embedding vector for text using Gemini"""
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return embeddings.embed_query(text)

def init_db(conn):
    cursor = conn.cursor()
    
    # Create recipes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ingredients JSON NOT NULL,
            difficulty TEXT NOT NULL,
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
    # Using 3072 dimensions for models/gemini-embedding-001
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_recipes USING vec0(
            recipe_id INTEGER PRIMARY KEY,
            embedding float[3072]
        )
    """)
    
    conn.commit()

def find_recipe_by_ingredients(conn, ingredients: List[str], difficulty: str):
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
    from config import filter_default_ingredients
    
    cursor = conn.cursor()
    # Filter out default ingredients and sort for consistent lookup
    non_default_ingredients = filter_default_ingredients(ingredients)
    ingredients_json = json.dumps(sorted(non_default_ingredients))
    
    cursor.execute("""
        SELECT * FROM recipes WHERE ingredients = ? AND difficulty = ?
    """, (ingredients_json, difficulty))
    
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None

def log_error(conn, error_type: str, message: str, request_id: str = None):
    """Log an error to the logs table"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (error_type, message, request_id)
        VALUES (?, ?, ?)
    """, (error_type, message, request_id))
    conn.commit()

def find_recipe_semantically(conn, ingredients: List[str], difficulty: str, threshold: float = 0.5):
    """
    Find a recipe using semantic similarity on ingredients + name.
    """
    query_text = f"Ingredients: {', '.join(sorted(ingredients))}"
    query_vector = generate_embedding(query_text)
    
    cursor = conn.cursor()
    # MATCH query for vec0 tables
    cursor.execute("""
        SELECT 
            r.*, 
            v.distance
        FROM vec_recipes v
        JOIN recipes r ON v.recipe_id = r.id
        WHERE v.embedding MATCH ? AND r.difficulty = ? AND k = 1
        ORDER BY v.distance
    """, (sqlite_vec.serialize_float32(query_vector), difficulty))
    
    row = cursor.fetchone()
    # If distance is too high, it might not be a good match
    if row and row['distance'] < threshold:
        return dict(row)
    return None

def save_recipe(conn, name: str, ingredients: List[str], difficulty: str, steps: List[str], metadata: Dict[str, Any] = None):
    """Save a recipe and its embedding to the database"""
    cursor = conn.cursor()
    
    # 1. Save to relational table
    cursor.execute("""
        INSERT INTO recipes (name, ingredients, difficulty, steps, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        json.dumps(sorted(ingredients)),
        difficulty,
        json.dumps(steps),
        json.dumps(metadata or {})
    ))
    recipe_id = cursor.lastrowid
    
    # 2. Generate and save embedding
    embedding_text = f"Ingredients: {', '.join(sorted(ingredients))}"
    embedding = generate_embedding(embedding_text)
    
    cursor.execute("""
        INSERT INTO vec_recipes (recipe_id, embedding)
        VALUES (?, ?)
    """, (recipe_id, sqlite_vec.serialize_float32(embedding)))
    
    conn.commit()
    return recipe_id
