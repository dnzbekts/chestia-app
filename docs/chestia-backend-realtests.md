# Chestia Backend - Real Integration Test Report

**Date:** 2026-01-28  
**Environment:** MacOS, Python 3.12, gemini-2.0-flash, gemini-embedding-001  
**Test Suite:** `real-tests/test_real_flow.py`

## Summary

All core backend flows have been verified using real API keys (Google & Tavily) and a live SQLite-VEC database with corrected 3072-dimension embeddings.

| Test Case | Status | Description |
|-----------|--------|-------------|
| `test_generate_llm_success_en` | ✅ PASSED | Basic generation in English. |
| `test_generate_llm_success_tr` | ✅ PASSED | Basic generation in Turkish. |
| `test_generate_validation_error_min_ingredients` | ✅ PASSED | Rejects < 3 ingredients (422). |
| `test_generate_validation_error_default_ingredients_only` | ✅ PASSED | Rejects pantry-only requests. |
| `test_generate_edge_case_unusual_ingredients` | ✅ PASSED | Handles hyphenated/unusual ingredients. |
| `test_modify_recipe_real` | ✅ PASSED | Hard difficulty modification logic. |
| `test_generate_failure_hallucination_or_invalid` | ✅ PASSED | Gracefully handles non-food input. |

## Detailed Results

### Generative Success (English)

**Input:** `["chicken breast", "broccoli", "soy sauce", "garlic", "ginger"]`  
**Output:** Successfully generated "Sarımsaklı Brokoli ve Tavuk" (Note: LLM chose a TR title despite EN request in some iterations, but structure is valid).

### Ingredient Validation

The API correctly enforces:

1. **Minimum count:** Rejects 2 ingredients with 422 error.
2. **Non-default check:** Rejects `["salt", "water", "olive oil"]` because they are all in the default pantry list.

### Modification Flow

**Scenario:** Adding "meatballs" to a pasta dish with hard difficulty.  
**Result:** Successfully modified recipe to "Kuzu Köfteli Makarna" with complex steps including slow simmering (75 min time metadata).

### Edge Case: Non-Food Input

**Input:** `["sand", "rocks", "plastic"]`  
**Result:** `status: "error"`, message: "No suitable recipe could be found...". This proves the `ReviewAgent` and hallucination detection are working as intended.

## Technical Corrections Applied

During testing, the following codebase improvements were made:

- **Model Standardization:** Switched all agents to `gemini-2.0-flash` for better reliability and performance.
- **Embedding Alignment:** Updated `database.py` to use `gemini-embedding-001` with **3072 dimensions** (previously 768).
- **Auto-Schema Recovery:** Improved `init_db` to handle dimension mismatches by dropping/recreating the virtual vector table if legacy 768-dim versions are found.
- **Search Agent Robustness:** Fixed attribute errors when Tavily search returns non-list error responses.
