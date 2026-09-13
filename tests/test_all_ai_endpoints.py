"""End-to-End Automated Verification Test Suite for Food AI Suite."""
import sys
import os

# Add parent directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_00_root_and_health():
    """Verify service health and routing."""
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "online"
    assert "/docs" in data["documentation"]

    r_health = client.get("/api/ai/health")
    assert r_health.status_code == 200
    health_data = r_health.json()
    assert health_data["status"] == "healthy"
    assert health_data["catalog_size"] > 0
    print("PASS: test_00_root_and_health")

def test_01_concierge():
    """Verify Conversational AI Concierge recommendations and mood extraction."""
    payload = {
        "prompt": "I want a spicy, comforting dinner under 500 for two with no dairy.",
        "user_preferences": {
            "dietary": ["Dairy"],
            "budget": 500.0,
            "cuisine_preference": "North Indian"
        }
    }
    r = client.post("/api/ai/concierge", json=payload)
    assert r.status_code == 200
    res = r.json()
    assert "reply" in res
    assert len(res["recommended_dishes"]) > 0
    assert "suggested_followups" in res
    # Verify no dairy was recommended
    for dish in res["recommended_dishes"]:
        assert "Dairy" not in dish["allergens"]
    print(f"PASS: test_01_concierge (Found {len(res['recommended_dishes'])} matching dishes)")

def test_02_visual_search():
    """Verify Visual Search multi-modal food recognition and macro breakdown."""
    payload = {
        "preset_dish_hint": "pizza"
    }
    r = client.post("/api/ai/visual-search", json=payload)
    assert r.status_code == 200
    res = r.json()
    assert "Truffle" in res["identified_dish"] or "Pizza" in res["identified_dish"]
    assert res["estimated_macros"]["calories"] > 0
    assert res["estimated_macros"]["protein_g"] > 0
    assert len(res["matching_catalog_items"]) > 0
    print(f"PASS: test_02_visual_search (Identified '{res['identified_dish']}' with {res['estimated_macros']['calories']} kcal)")

def test_03_smart_cart():
    """Verify Smart Cart dynamic pairing upsells and allergen conflict alerts."""
    # Cart contains Paneer Butter Masala (dish_1) and Naan (dish_2)
    # User is Dairy intolerant
    payload = {
        "cart_item_ids": ["dish_1", "dish_2"],
        "user_dietary_restrictions": ["Dairy"]
    }
    r = client.post("/api/ai/smart-cart", json=payload)
    assert r.status_code == 200
    res = r.json()
    assert res["cart_items_count"] == 2
    assert len(res["pairing_suggestions"]) > 0
    # Allergen alert should be triggered because dish_1 contains Dairy
    assert len(res["safety_alerts"]) > 0
    assert any("Dairy" in a["conflict_type"] for a in res["safety_alerts"])
    assert res["nutrition_summary"]["total_calories"] > 0
    print(f"PASS: test_03_smart_cart (Triggered {len(res['safety_alerts'])} allergen alerts, {len(res['pairing_suggestions'])} pairing suggestions)")

def test_04_menu_copilot():
    """Verify Merchant Menu Copilot generates gourmet copy, tags, and pricing benchmarks."""
    payload = {
        "dish_name": "Smoked Truffle Risotto",
        "cuisine": "Italian",
        "key_ingredients": ["Arborio Rice", "Porcini Mushrooms", "Black Truffle Oil", "Parmigiano Reggiano"],
        "target_vibe": "Gourmet"
    }
    r = client.post("/api/ai/menu-copilot", json=payload)
    assert r.status_code == 200
    res = r.json()
    assert res["dish_name"] == "Smoked Truffle Risotto"
    assert "gourmet_editorial" in res["descriptions"]
    assert len(res["culinary_tags"]) > 0
    assert "Dairy" in res["detected_allergens"]
    assert res["pricing_benchmark"]["recommended_price"] > 0
    assert "social_media_hook" in res
    print(f"PASS: test_04_menu_copilot (Generated 3 descriptions, benchmark: INR {res['pricing_benchmark']['recommended_price']})")

def test_05_review_sentiment():
    """Verify Aspect-based review sentiment NLP analysis and tailored auto-responder."""
    payload = {
        "reviews": [
            {
                "id": "rev_1",
                "customer_name": "Aarav S.",
                "rating": 5.0,
                "text": "The paneer butter masala was absolutely delicious and piping hot! Best gravy in town."
            },
            {
                "id": "rev_2",
                "customer_name": "Neha K.",
                "rating": 2.0,
                "text": "Delivery was late and the curry container leaked inside the bag. Very messy."
            }
        ]
    }
    r = client.post("/api/ai/review-sentiment", json=payload)
    assert r.status_code == 200
    res = r.json()
    assert res["total_reviews_analyzed"] == 2
    assert res["aspect_scores"]["taste_and_flavor"] >= 4.0
    assert res["aspect_scores"]["packaging_integrity"] <= 3.0
    assert len(res["suggested_replies"]) == 2
    assert any(reply["reply_tone"] == "Empathetic" for reply in res["suggested_replies"])
    assert any(reply["reply_tone"] == "Celebratory" for reply in res["suggested_replies"])
    print(f"PASS: test_05_review_sentiment (Analyzed aspects, generated {len(res['suggested_replies'])} targeted replies)")

def test_06_event_dining_bundler():
    """Verify Night-Out Event + Dining Itinerary Planner."""
    payload = {
        "event_id": "event_1",
        "party_size": 2,
        "dining_vibe": "Romantic",
        "timing_preference": "PRE_EVENT"
    }
    r = client.post("/api/ai/event-dining-bundler", json=payload)
    assert r.status_code == 200
    res = r.json()
    assert "event_title" in res
    assert "dining_recommendation" in res
    assert len(res["timeline"]) >= 3
    assert res["total_estimated_budget"] > 0
    print(f"PASS: test_06_event_dining_bundler (Curated itinerary for '{res['event_title']}', budget: INR {res['total_estimated_budget']})")

def test_07_predict_eta():
    """Verify Dynamic Kitchen & Logistics Delivery ETA engine."""
    payload = {
        "order_item_count": 4,
        "dish_complexity_score": 4,
        "kitchen_current_queue": 8,
        "distance_km": 5.2,
        "weather_condition": "RAIN",
        "traffic_level": "HEAVY"
    }
    r = client.post("/api/ai/predict-eta", json=payload)
    assert r.status_code == 200
    res = r.json()
    assert res["predicted_eta_minutes"] >= 30
    assert res["confidence_interval"]["min_eta_minutes"] < res["predicted_eta_minutes"]
    assert res["confidence_interval"]["max_eta_minutes"] > res["predicted_eta_minutes"]
    assert res["factors_breakdown"]["weather_delay_minutes"] > 0
    assert len(res["delay_warnings"]) > 0
    print(f"PASS: test_07_predict_eta (Predicted ETA: {res['predicted_eta_minutes']} mins with weather & traffic surge)")

if __name__ == "__main__":
    print("\n--- Running Food AI Suite Automated Test Suite ---")
    test_00_root_and_health()
    test_01_concierge()
    test_02_visual_search()
    test_03_smart_cart()
    test_04_menu_copilot()
    test_05_review_sentiment()
    test_06_event_dining_bundler()
    test_07_predict_eta()
    print("\n*** ALL 8 AI VERIFICATION TESTS PASSED SUCCESSFULLY! ***\n")
