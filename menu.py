import logging
from database import get_all_menu_items

logger = logging.getLogger(__name__)

def find_menu_item(item_name, threshold=20):
    """
    Find a menu item by name using improved fuzzy matching.
    
    Args:
        item_name: The name to search for
        threshold: Minimum match score to consider a match
    
    Returns:
        Best matching menu item or None if no good match
    """
    if not item_name:
        return None
    
    item_name = item_name.lower().strip()
    all_items = get_all_menu_items()
    
    # Early return for exact matches
    for item in all_items:
        if item["name"].lower() == item_name:
            return item
    
    # Initialize best match tracking
    best_match = None
    best_score = threshold
    
    # Check all menu items with improved scoring
    for item in all_items:
        item_lower = item["name"].lower()
        score = 0
        
        # 1. Contains entire phrase
        if item_name in item_lower:
            score = 80
        
        # 2. Item name contains the search term
        elif item_lower in item_name:
            score = 70
        
        # 3. Word-by-word matching
        else:
            item_words = set(item_lower.split())
            name_words = set(item_name.split())
            common_words = item_words.intersection(name_words)
            
            # If all words in search match
            if common_words == name_words:
                score = 60
            # If all words in item match
            elif common_words == item_words:
                score = 50
            # Partial word matching
            elif common_words:
                # Score based on percentage of matching words
                score = 40 * len(common_words) / max(len(item_words), len(name_words))
        
        # Update best match if score is higher
        if score > best_score:
            best_match = item
            best_score = score
    
    return best_match

def prepare_menu_info():
    """Prepare formatted menu information for prompts."""
    menu_items = get_all_menu_items()
    menu_by_category = {}
    for item in menu_items:
        category = item["category"]
        if category not in menu_by_category:
            menu_by_category[category] = []
        menu_by_category[category].append(item)
    
    menu_info = "Shake Shack Menu Information:\n"
    for category, items in menu_by_category.items():
        menu_info += f"\n{category}:\n"
        for item in items:
            menu_info += f"- {item['name']}: ${item['price']:.2f}, {item['calories']} calories\n"
    
    return menu_info

def display_formatted_menu():
    """
    Returns a nicely formatted menu for display to the user.
    This is separate from prepare_menu_info which is for LLM prompts.
    """
    menu_items = get_all_menu_items()
    menu_by_category = {}
    for item in menu_items:
        category = item["category"]
        if category not in menu_by_category:
            menu_by_category[category] = []
        menu_by_category[category].append(item)
    
    formatted_menu = "# Shake Shack Menu\n\n"
    for category, items in menu_by_category.items():
        formatted_menu += f"## {category}\n\n"
        for item in items:
            formatted_menu += f"- **{item['name']}** — ${item['price']:.2f} ({item['calories']} calories)\n"
        formatted_menu += "\n"
    
    return formatted_menu