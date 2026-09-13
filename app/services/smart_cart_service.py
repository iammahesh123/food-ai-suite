"""Smart Cart Dynamic Pairing and Allergen / Dietary Safety Guard Service."""
from typing import List, Dict, Any
from app.models.schemas import (
    SmartCartRequest,
    SmartCartResponse,
    PairingSuggestion,
    DietarySafetyAlert,
    CartNutritionSummary
)
from app.data.catalog import get_dish_by_id, CATALOG_ITEMS

def run_smart_cart_ai(request: SmartCartRequest) -> SmartCartResponse:
    cart_items = [get_dish_by_id(item_id) for item_id in request.cart_item_ids]
    cart_items = [item for item in cart_items if item is not None]

    # 1. Nutrition Summary calculation
    total_cal = sum(item["calories"] for item in cart_items)
    total_protein = sum(item["protein_g"] for item in cart_items)
    total_carbs = sum(item["carbs_g"] for item in cart_items)
    total_fat = sum(item["fat_g"] for item in cart_items)

    nutrition_summary = CartNutritionSummary(
        total_calories=int(total_cal),
        total_protein_g=float(round(total_protein, 1)),
        total_carbs_g=float(round(total_carbs, 1)),
        total_fat_g=float(round(total_fat, 1))
    )

    # 2. Dietary & Allergen Safety Guard
    user_restrictions = [r.strip().lower() for r in request.user_dietary_restrictions or []]
    safety_alerts: List[DietarySafetyAlert] = []

    for item in cart_items:
        # Check explicit allergens
        for allergen in item.get("allergens", []):
            if allergen.lower() in user_restrictions:
                safety_alerts.append(
                    DietarySafetyAlert(
                        dish_id=item["id"],
                        dish_name=item["name"],
                        conflict_type=f"Allergen: {allergen}",
                        severity="HIGH",
                        warning_message=f"Contains {allergen}, which conflicts with your stated allergy restriction."
                    )
                )

        # Check Vegan restriction
        if "vegan" in user_restrictions and not item.get("is_vegan", False):
            safety_alerts.append(
                DietarySafetyAlert(
                    dish_id=item["id"],
                    dish_name=item["name"],
                    conflict_type="Diet: Non-Vegan",
                    severity="HIGH",
                    warning_message="This item contains animal byproducts (such as dairy or butter) and is not 100% vegan."
                )
            )

        # Check Gluten-Free restriction
        if "gluten-free" in user_restrictions or "gluten" in user_restrictions:
            if not item.get("is_gluten_free", False):
                safety_alerts.append(
                    DietarySafetyAlert(
                        dish_id=item["id"],
                        dish_name=item["name"],
                        conflict_type="Diet: Gluten Present",
                        severity="HIGH",
                        warning_message="Contains wheat/gluten ingredients."
                    )
                )

    # 3. Dynamic Pairing Suggestions
    existing_ids = set(request.cart_item_ids)
    candidate_pairings: Dict[str, str] = {}

    for item in cart_items:
        for paired_id in item.get("pairings", []):
            if paired_id not in existing_ids:
                paired_dish = get_dish_by_id(paired_id)
                if paired_dish:
                    reason = f"Culinary complement: Pairs naturally with {item['name']}"
                    candidate_pairings[paired_id] = reason

    # If no natural graph pairings, add a refreshing beverage or popular side
    if not candidate_pairings:
        candidate_pairings["dish_10"] = "Refreshing palate cleanser: Organic passionfruit kombucha"
        candidate_pairings["dish_7"] = "Crowd-favorite crispy truffle fries to complete the spread"

    pairing_suggestions: List[PairingSuggestion] = []
    for pid, reason in list(candidate_pairings.items())[:3]:
        pdish = get_dish_by_id(pid)
        if pdish:
            pairing_suggestions.append(
                PairingSuggestion(
                    dish_id=pdish["id"],
                    name=pdish["name"],
                    price=float(pdish["price"]),
                    pairing_reason=reason
                )
            )

    upsell_note = "Dishes in your cart have high flavor affinity with artisanal breads and digestive beverages."

    return SmartCartResponse(
        cart_items_count=len(cart_items),
        pairing_suggestions=pairing_suggestions,
        safety_alerts=safety_alerts,
        nutrition_summary=nutrition_summary,
        smart_upsell_reason=upsell_note
    )
