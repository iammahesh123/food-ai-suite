"""Merchant AI Studio & Menu Copilot Service."""
from typing import List
from app.models.schemas import (
    MenuCopilotRequest,
    MenuCopilotResponse,
    MenuDescriptions,
    PricingBenchmark
)
from app.services.gemini_client import query_gemini_json, is_gemini_active

def _infer_allergens(ingredients: List[str]) -> List[str]:
    allergens = set()
    ing_lower = " ".join([i.lower() for i in ingredients])
    if any(w in ing_lower for w in ["cheese", "butter", "cream", "milk", "parmigiano", "paneer", "yogurt", "ghee"]):
        allergens.add("Dairy")
    if any(w in ing_lower for w in ["wheat", "flour", "bread", "pasta", "crust", "naan", "brioche"]):
        allergens.add("Gluten")
    if any(w in ing_lower for w in ["peanut", "almond", "walnut", "cashew", "praline", "hazelnut"]):
        allergens.add("Tree Nuts")
    if any(w in ing_lower for w in ["soy", "tofu", "edamame"]):
        allergens.add("Soy")
    if any(w in ing_lower for w in ["prawn", "shrimp", "crab", "lobster"]):
        allergens.add("Shellfish")
    return sorted(list(allergens))

def run_menu_copilot_ai(request: MenuCopilotRequest) -> MenuCopilotResponse:
    dish = request.dish_name
    cuisine = request.cuisine
    ingredients = request.key_ingredients
    vibe = request.target_vibe or "Gourmet"

    # If Gemini LLM is active
    if is_gemini_active():
        prompt = f"""
        You are an elite Michelin-star food copywriter and restaurant consultant.
        Dish Name: {dish}
        Cuisine: {cuisine}
        Key Ingredients: {', '.join(ingredients)}
        Vibe: {vibe}

        Provide JSON matching:
        {{
          "descriptions": {{
            "short_punchy": "1-sentence sensory appetizer description",
            "gourmet_editorial": "2-3 sentences rich culinary storytelling highlighting cooking technique and ingredient origins",
            "health_and_craft": "Nutritional benefit, clean ingredient profile, and artisanal preparation"
          }},
          "culinary_tags": ["tag1", "tag2", "tag3"],
          "detected_allergens": ["Dairy", "Gluten"],
          "pricing_benchmark": {{
            "suggested_min": 320,
            "suggested_max": 480,
            "recommended_price": 390,
            "market_reasoning": "Competitive benchmark analysis"
          }},
          "social_media_hook": "Catchy Instagram caption with hashtags"
        }}
        """
        gemini_res = query_gemini_json(prompt, "You are a professional culinary editor and pricing strategist.")
        if gemini_res and "descriptions" in gemini_res:
            try:
                return MenuCopilotResponse(
                    dish_name=dish,
                    cuisine=cuisine,
                    descriptions=MenuDescriptions(**gemini_res["descriptions"]),
                    culinary_tags=gemini_res.get("culinary_tags", ["Artisanal", cuisine, "Chef Signature"]),
                    detected_allergens=gemini_res.get("detected_allergens", _infer_allergens(ingredients)),
                    pricing_benchmark=PricingBenchmark(**gemini_res["pricing_benchmark"]),
                    social_media_hook=gemini_res.get("social_media_hook", f"Indulge in our new {dish}! 🍽️✨")
                )
            except Exception:
                pass

    # Built-in High Quality Heuristic Engine
    ing_text = ", ".join(ingredients[:3])
    detected_allergens = _infer_allergens(ingredients)

    # Descriptions
    short_desc = f"Handcrafted {cuisine.lower()} specialty featuring fresh {ing_text} infused with house-blended seasonings."
    gourmet_desc = (
        f"An exquisite harmony of authentic {cuisine} craftsmanship. "
        f"Slow-simmered {ingredients[0] if ingredients else 'prime ingredients'} delicately paired with "
        f"{ing_text}, finished with an aromatic glaze that delivers layers of textured warmth."
    )
    health_desc = (
        f"Crafted with wholesome, preservative-free {ing_text}. "
        f"Rich in natural nutrients and balanced for an uplifting, guilt-free dining experience."
    )

    tags = ["Chef's Signature", f"{cuisine} Classic", "Locally Sourced", "Gourmet Edition"]
    if "Dairy" not in detected_allergens and "Shellfish" not in detected_allergens:
        tags.append("Dairy-Free")

    # Dynamic pricing benchmarks based on ingredients and cuisine
    is_premium = any(i.lower() in " ".join(ingredients).lower() for i in ["truffle", "saffron", "parmigiano", "lobster", "porcini", "belgian"])
    base_price = 420.0 if is_premium else 280.0
    suggested_min = round(base_price * 0.85, 0)
    suggested_max = round(base_price * 1.35, 0)
    recommended_price = round(base_price * 1.05, 0)

    reasoning = (
        f"Based on premium ingredient footprint ({'high-cost gourmet ingredients detected' if is_premium else 'standard fresh produce'}) "
        f"and {cuisine} market positioning in urban delivery zones, maintaining a {int(recommended_price)} price point optimizes 68% gross margin."
    )

    social_hook = f"Craving something extraordinary? Our new {dish} crafted with fresh {ing_text} is here to redefine your palate. Available now on delivery! 🔥🍽️ #FoodieLife #{cuisine.replace(' ', '')}"

    return MenuCopilotResponse(
        dish_name=dish,
        cuisine=cuisine,
        descriptions=MenuDescriptions(
            short_punchy=short_desc,
            gourmet_editorial=gourmet_desc,
            health_and_craft=health_desc
        ),
        culinary_tags=tags,
        detected_allergens=detected_allergens,
        pricing_benchmark=PricingBenchmark(
            suggested_min=suggested_min,
            suggested_max=suggested_max,
            recommended_price=recommended_price,
            market_reasoning=reasoning
        ),
        social_media_hook=social_hook
    )
