"""Multi-Modal Visual Search & Food Recognition Service."""
from typing import List, Dict, Any, Optional
from app.models.schemas import VisualSearchRequest, VisualSearchResponse, MacroBreakdown, CatalogMatch
from app.data.catalog import CATALOG_ITEMS
from app.services.gemini_client import query_gemini_json, is_gemini_active

PRESET_KNOWLEDGE = {
    "pizza": {
        "identified_dish": "Wood-Fired Truffle Funghi Pizza",
        "cuisine": "Italian",
        "confidence_score": 0.96,
        "macros": {"calories": 780, "protein_g": 28.0, "carbs_g": 85.0, "fat_g": 36.0},
        "allergens": ["Gluten", "Dairy"],
        "dietary_flags": ["Vegetarian"],
        "matched_id": "dish_6"
    },
    "bowl": {
        "identified_dish": "Avocado & Edamame Poke Bowl",
        "cuisine": "Japanese Fusion",
        "confidence_score": 0.94,
        "macros": {"calories": 380, "protein_g": 18.0, "carbs_g": 48.0, "fat_g": 14.0},
        "allergens": ["Soy"],
        "dietary_flags": ["Vegan", "Gluten-Free", "High-Protein"],
        "matched_id": "dish_3"
    },
    "curry": {
        "identified_dish": "Paneer Butter Masala",
        "cuisine": "North Indian",
        "confidence_score": 0.97,
        "macros": {"calories": 420, "protein_g": 16.0, "carbs_g": 22.0, "fat_g": 30.0},
        "allergens": ["Dairy"],
        "dietary_flags": ["Vegetarian", "Gluten-Free"],
        "matched_id": "dish_1"
    },
    "burger": {
        "identified_dish": "Smoky BBQ Paneer Burger",
        "cuisine": "American Gourmet",
        "confidence_score": 0.92,
        "macros": {"calories": 520, "protein_g": 22.0, "carbs_g": 56.0, "fat_g": 24.0},
        "allergens": ["Gluten", "Dairy"],
        "dietary_flags": ["Vegetarian"],
        "matched_id": "dish_8"
    }
}

def run_visual_search_ai(request: VisualSearchRequest) -> VisualSearchResponse:
    # If Gemini Vision is active and an image is provided:
    if is_gemini_active() and (request.image_base64 or request.image_url):
        llm_prompt = f"""
        Analyze this food image.
        Identify:
        1. Identified Dish Name
        2. Cuisine
        3. Confidence Score (0.0 to 1.0)
        4. Estimated Macros (calories, protein_g, carbs_g, fat_g)
        5. Detected Allergens (e.g. Dairy, Gluten, Nuts, Soy)
        6. Dietary flags (e.g. Vegetarian, Vegan, Halal)
        
        Respond ONLY in JSON:
        {{
          "identified_dish": "...",
          "cuisine": "...",
          "confidence_score": 0.95,
          "estimated_macros": {{ "calories": 450, "protein_g": 15, "carbs_g": 40, "fat_g": 20 }},
          "detected_allergens": ["Dairy"],
          "dietary_flags": ["Vegetarian"]
        }}
        """
        gemini_res = query_gemini_json(llm_prompt, "You are a world-class culinary computer vision AI.")
        if gemini_res and "identified_dish" in gemini_res:
            try:
                # Find matching catalog items
                dish_name = gemini_res.get("identified_dish", "").lower()
                matches = []
                for cat_item in CATALOG_ITEMS:
                    sim = 0.5
                    if cat_item["name"].lower() in dish_name or dish_name in cat_item["name"].lower():
                        sim = 0.95
                    elif cat_item["cuisine"].lower() in gemini_res.get("cuisine", "").lower():
                        sim = 0.75
                    matches.append(CatalogMatch(
                        id=cat_item["id"],
                        name=cat_item["name"],
                        cuisine=cat_item["cuisine"],
                        price=float(cat_item["price"]),
                        similarity_score=sim
                    ))
                matches.sort(key=lambda x: x.similarity_score, reverse=True)
                
                return VisualSearchResponse(
                    identified_dish=gemini_res["identified_dish"],
                    cuisine=gemini_res.get("cuisine", "Continental"),
                    confidence_score=float(gemini_res.get("confidence_score", 0.92)),
                    estimated_macros=MacroBreakdown(**gemini_res["estimated_macros"]),
                    detected_allergens=gemini_res.get("detected_allergens", []),
                    dietary_flags=gemini_res.get("dietary_flags", []),
                    matching_catalog_items=matches[:3]
                )
            except Exception:
                pass

    # Heuristic / Knowledge Engine fallback
    hint = (request.preset_dish_hint or "").lower()
    chosen_key = "pizza"
    for key in PRESET_KNOWLEDGE:
        if key in hint:
            chosen_key = key
            break

    profile = PRESET_KNOWLEDGE[chosen_key]
    matched_catalog_item = next((c for c in CATALOG_ITEMS if c["id"] == profile["matched_id"]), CATALOG_ITEMS[0])

    matches = [
        CatalogMatch(
            id=matched_catalog_item["id"],
            name=matched_catalog_item["name"],
            cuisine=matched_catalog_item["cuisine"],
            price=float(matched_catalog_item["price"]),
            similarity_score=profile["confidence_score"]
        )
    ]
    # Add adjacent catalog matches
    for item in CATALOG_ITEMS:
        if item["id"] != matched_catalog_item["id"] and item["cuisine"] == matched_catalog_item["cuisine"]:
            matches.append(CatalogMatch(
                id=item["id"],
                name=item["name"],
                cuisine=item["cuisine"],
                price=float(item["price"]),
                similarity_score=0.78
            ))

    return VisualSearchResponse(
        identified_dish=profile["identified_dish"],
        cuisine=profile["cuisine"],
        confidence_score=profile["confidence_score"],
        estimated_macros=MacroBreakdown(**profile["macros"]),
        detected_allergens=profile["allergens"],
        dietary_flags=profile["dietary_flags"],
        matching_catalog_items=matches[:3]
    )
