from typing import Dict, Literal

# Message keys
MIN_INGREDIENTS = "min_ingredients"
RECIPE_NOT_FOUND = "recipe_not_found"
GENERATION_ERROR = "generation_error"
INTERNAL_SERVER_ERROR = "internal_server_error"
FEEDBACK_SUCCESS = "feedback_success"
FEEDBACK_REJECTED = "feedback_rejected"
FEEDBACK_SAVE_FAILED = "feedback_save_failed"

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
