from typing import Dict, Literal

# Message keys
MIN_INGREDIENTS = "min_ingredients"
RECIPE_NOT_FOUND = "recipe_not_found"
GENERATION_ERROR = "generation_error"
INTERNAL_SERVER_ERROR = "internal_server_error"
FEEDBACK_SUCCESS = "feedback_success"
FEEDBACK_REJECTED = "feedback_rejected"
FEEDBACK_SAVE_FAILED = "feedback_save_failed"
SEARCHING_CACHE = "searching_cache"
RECIPE_VALIDATED = "recipe_validated"
GENERATING_RECIPE = "generating_recipe"
SEMANTIC_SEARCH_HIT = "semantic_search_hit"
SEMANTIC_SEARCH_MISS = "semantic_search_miss"
WEB_SEARCH_HIT = "web_search_hit"
WEB_SEARCH_MISS = "web_search_miss"

MESSAGES: Dict[str, Dict[str, str]] = {
    MIN_INGREDIENTS: {
        "en": "At least one non-default ingredient is required (ingredients like water, salt, and oil do not count)",
        "tr": "En az bir adet default olmayan malzeme gerekli (su, tuz ve yağ gibi malzemeler sayılmaz)"
    },
    RECIPE_NOT_FOUND: {
        "en": "No suitable recipe could be found with the ingredients you provided. Please try again with different ingredients.",
        "tr": "İlettiğiniz malzemelerle uygun bir tarif bulunamadı. Lütfen farklı malzemelerle tekrar deneyin."
    },
    GENERATION_ERROR: {
        "en": "Unable to process your request at this time",
        "tr": "İsteğiniz şu anda işlenemiyor"
    },
    INTERNAL_SERVER_ERROR: {
        "en": "Internal Server Error",
        "tr": "Sunucu Hatası"
    },
    FEEDBACK_SUCCESS: {
        "en": "Recipe saved successfully",
        "tr": "Tarif başarıyla kaydedildi"
    },
    FEEDBACK_REJECTED: {
        "en": "Please try again with different ingredients.",
        "tr": "Lütfen farklı malzemelerle tekrar deneyin."
    },
    FEEDBACK_SAVE_FAILED: {
        "en": "Failed to save your feedback",
        "tr": "Geri bildiriminiz kaydedilemedi"
    },
    SEARCHING_CACHE: {
        "en": "Checking if we have a similar recipe in our cookbook...",
        "tr": "Kitabımızda benzer bir tarif olup olmadığını kontrol ediyorum..."
    },
    RECIPE_VALIDATED: {
        "en": "Recipe looks delicious and follows all rules!",
        "tr": "Tarif harika görünüyor ve tüm kurallara uygun!"
    },
    GENERATING_RECIPE: {
        "en": "Creating a new recipe just for you...",
        "tr": "Sizin için yeni bir tarif oluşturuyorum..."
    },
    SEMANTIC_SEARCH_HIT: {
        "en": "Found a very similar recipe in our collection!",
        "tr": "Koleksiyonumuzda çok benzer bir tarif buldum!"
    },
    SEMANTIC_SEARCH_MISS: {
        "en": "No similar recipes found locally, searching broader...",
        "tr": "Benzer tarif bulunamadı, daha geniş kapsamlı arıyorum..."
    },
    WEB_SEARCH_HIT: {
        "en": "Found a great recipe from our web search!",
        "tr": "Web aramamızda harika bir tarif buldum!"
    },
    WEB_SEARCH_MISS: {
        "en": "No recipes found online, I will create one from scratch.",
        "tr": "Çevrimiçi tarif bulunamadı, sıfırdan bir tane oluşturacağım."
    }
}

def get_message(key: str, lang: str = "en") -> str:
    """
    Retrieve a bilingual message by key and language.
    
    Args:
        key: The message key (defined above)
        lang: Language code ('en' or 'tr')
        
    Returns:
        The message string in the requested language, defaults to English.
    """
    # Ensure lang is supported, fallback to 'en'
    if lang not in ["en", "tr"]:
        lang = "en"
    
    message_entry = MESSAGES.get(key)
    if not message_entry:
        return f"Message key '{key}' not found"
        
    return message_entry.get(lang, message_entry.get("en", "Message not found"))
