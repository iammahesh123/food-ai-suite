"""Customer Review Sentiment & Feedback Auto-Responder Service."""
from typing import List
from app.models.schemas import (
    ReviewSentimentRequest,
    ReviewSentimentResponse,
    AspectScores,
    SuggestedReply
)
from app.services.gemini_client import query_gemini_json, is_gemini_active

def run_sentiment_ai(request: ReviewSentimentRequest) -> ReviewSentimentResponse:
    reviews = request.reviews
    if not reviews:
        return ReviewSentimentResponse(
            total_reviews_analyzed=0,
            overall_sentiment_score=5.0,
            aspect_scores=AspectScores(
                taste_and_flavor=5.0,
                delivery_and_temp=5.0,
                packaging_integrity=5.0,
                value_for_money=5.0
            ),
            praise_highlights=[],
            critical_pain_points=[],
            suggested_replies=[]
        )

    # If Gemini LLM is active
    if is_gemini_active():
        prompt = f"""
        Analyze these customer reviews for a food business:
        {[r.dict() for r in reviews]}

        Perform Aspect-based sentiment analysis on a 1.0 to 5.0 scale for:
        1. taste_and_flavor
        2. delivery_and_temp
        3. packaging_integrity
        4. value_for_money

        Provide JSON:
        {{
          "overall_sentiment_score": 4.5,
          "aspect_scores": {{
            "taste_and_flavor": 4.8,
            "delivery_and_temp": 4.2,
            "packaging_integrity": 3.9,
            "value_for_money": 4.4
          }},
          "praise_highlights": ["Highlight 1", "Highlight 2"],
          "critical_pain_points": ["Pain point 1"],
          "suggested_replies": [
             {{
               "review_id": "rev_1",
               "customer_name": "...",
               "reply_tone": "Empathetic",
               "draft_response": "..."
             }}
          ]
        }}
        """
        gemini_res = query_gemini_json(prompt, "You are a customer experience NLP intelligence analyst.")
        if gemini_res and "aspect_scores" in gemini_res:
            try:
                replies = [SuggestedReply(**r) for r in gemini_res.get("suggested_replies", [])]
                return ReviewSentimentResponse(
                    total_reviews_analyzed=len(reviews),
                    overall_sentiment_score=float(gemini_res.get("overall_sentiment_score", 4.5)),
                    aspect_scores=AspectScores(**gemini_res["aspect_scores"]),
                    praise_highlights=gemini_res.get("praise_highlights", []),
                    critical_pain_points=gemini_res.get("critical_pain_points", []),
                    suggested_replies=replies
                )
            except Exception:
                pass

    # Built-in Aspect-based NLP Analysis
    taste_scores, delivery_scores, packaging_scores, value_scores = [], [], [], []
    praises, pain_points = [], []
    replies: List[SuggestedReply] = []

    for r in reviews:
        t = r.text.lower()
        rating = r.rating

        # Taste check
        if any(w in t for w in ["delicious", "tasty", "fresh", "flavor", "mouthwatering", "good food", "loved the"]):
            taste_scores.append(min(5.0, rating + 0.5))
            praises.append(f"Customers appreciate exceptional food flavor and recipe seasoning ({r.customer_name})")
        elif any(w in t for w in ["bland", "cold", "salty", "stale", "chewy", "bad food", "spoiled"]):
            taste_scores.append(max(1.0, rating - 0.5))
            pain_points.append(f"Texture or temperature dissatisfaction in dish delivery ({r.customer_name})")

        # Delivery & Temp
        if any(w in t for w in ["late", "delayed", "slow", "cold"]):
            delivery_scores.append(max(1.0, rating - 1.0))
            pain_points.append(f"Transit delays or courier handling time mentioned ({r.customer_name})")
        elif any(w in t for w in ["quick", "fast", "hot", "piping"]):
            delivery_scores.append(min(5.0, rating + 0.5))
            praises.append(f"Piping-hot delivery transit praised ({r.customer_name})")

        # Packaging
        if any(w in t for w in ["spill", "leak", "box", "soggy", "mess", "leaked"]):
            packaging_scores.append(max(1.0, rating - 1.2))
            pain_points.append(f"Packaging containment issue noted ({r.customer_name})")
        elif any(w in t for w in ["sealed", "neat", "packaging", "tamper"]):
            packaging_scores.append(min(5.0, rating + 0.5))

        # Value
        if any(w in t for w in ["expensive", "overpriced", "portion small"]):
            value_scores.append(max(1.0, rating - 0.8))
            pain_points.append(f"Portion-to-price perception concerns ({r.customer_name})")
        elif any(w in t for w in ["worth", "reasonable", "generous portion", "great value"]):
            value_scores.append(min(5.0, rating + 0.5))

        # Generate contextual auto-response
        if rating <= 2.5:
            tone = "Empathetic"
            draft = (
                f"Dear {r.customer_name}, we are truly sorry that your experience fell short of our standards. "
                f"We have flagged your feedback with our culinary and logistics team immediately to rectify this. "
                f"Please allow us to make this right on your next order with a complimentary upgrade."
            )
        elif rating >= 4.5:
            tone = "Celebratory"
            draft = (
                f"Hi {r.customer_name}! Thank you so much for the glowing review and five stars! ⭐ "
                f"We are thrilled you enjoyed the food. Our kitchen team can't wait to serve you again soon!"
            )
        else:
            tone = "Professional"
            draft = (
                f"Hi {r.customer_name}, thank you for your candid feedback. We are pleased you enjoyed elements of your meal, "
                f"and we are actively refining our preparation and packaging to make your next experience a full 5 stars!"
            )

        replies.append(
            SuggestedReply(
                review_id=r.id,
                customer_name=r.customer_name,
                reply_tone=tone,
                draft_response=draft
            )
        )

    def avg(lst: List[float]) -> float:
        return round(sum(lst) / len(lst), 1) if lst else 4.0

    avg_taste = avg(taste_scores)
    avg_delivery = avg(delivery_scores)
    avg_pkg = avg(packaging_scores)
    avg_val = avg(value_scores)
    overall = round((avg_taste + avg_delivery + avg_pkg + avg_val) / 4.0, 1)

    # Deduplicate highlights
    praises = list(dict.fromkeys(praises))[:3]
    pain_points = list(dict.fromkeys(pain_points))[:3]

    if not praises:
        praises = ["Consistent baseline satisfaction across standard order items"]
    if not pain_points:
        pain_points = ["No severe operational anomalies reported in this batch"]

    return ReviewSentimentResponse(
        total_reviews_analyzed=len(reviews),
        overall_sentiment_score=overall,
        aspect_scores=AspectScores(
            taste_and_flavor=avg_taste,
            delivery_and_temp=avg_delivery,
            packaging_integrity=avg_pkg,
            value_for_money=avg_val
        ),
        praise_highlights=praises,
        critical_pain_points=pain_points,
        suggested_replies=replies
    )
