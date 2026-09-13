# Food AI Suite 🧠🍽️

A pure AI microservice & backend intelligence engine for modern Food Delivery, Table Dining, and Live Event platforms. Built with **Python 3.12**, **FastAPI**, **Pydantic v2**, and **Google Gemini AI**.

**Strictly backend AI functionalities with zero UI code.**

---

## 🌟 7 Core AI Capabilities

1. **TasteBot AI Concierge (`POST /api/ai/concierge`)**:
   Understands natural language food cravings, budget constraints, dietary restrictions (e.g. Dairy-free, Vegan), and returns structured, scored dish recommendations with mood analysis and interactive follow-ups.

2. **Snap & Crave Visual Search (`POST /api/ai/visual-search`)**:
   Multi-modal food recognition from image data (or preset identifiers). Identifies dish name, regional cuisine, confidence score, full macro breakdown (calories, protein, carbs, fats), detected allergens, and matches to partner restaurant menu items.

3. **Smart Cart & Safety Guard (`POST /api/ai/smart-cart`)**:
   Real-time dynamic pairing recommendations (e.g., matching artisanal breads, palate-cleansing probiotic beverages), nutrition macro aggregation, and proactive dietary/allergen conflict warnings.

4. **Merchant AI Menu Copilot (`POST /api/ai/menu-copilot`)**:
   Generates mouth-watering descriptions across 3 editorial styles (Short & Punchy, Gourmet Storytelling, Health & Craft), culinary tags, allergen classifications, competitive pricing benchmarks, and social media captions.

5. **Customer Review Sentiment & Auto-Responder (`POST /api/ai/review-sentiment`)**:
   Aspect-based sentiment analysis across 4 key dimensions: *Taste & Flavor*, *Delivery & Temp*, *Packaging Integrity*, and *Value for Money*. Detects praise highlights, pain points, and automatically drafts tailored responses with tone selection (Empathetic, Celebratory, Professional).

6. **Night-Out Event & Dining Bundler (`POST /api/ai/event-dining-bundler`)**:
   Seamlessly bundles live events (concerts, comedy shows) with nearby table reservations, creating an optimized chronological timeline, travel estimates, and combined budget calculations.

7. **Predictive Kitchen & Logistics ETA Engine (`POST /api/ai/predict-eta`)**:
   Calculates realistic delivery arrival times factoring in live kitchen queue congestion, dish complexity score (1-5), transit distance, weather disruptions (e.g., Rain/Storm), and traffic density.

---

## 🚀 Quickstart & Running Locally

### 1. Activate Environment & Install Dependencies
```bash
# If using the project's virtual environment:
..\venv\Scripts\activate

# Or install dependencies:
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env`:
```env
PORT=8000
HOST=0.0.0.0
GEMINI_API_KEY=your_google_gemini_api_key  # Optional: Has built-in intelligent fallback
GEMINI_MODEL=gemini-2.5-flash
```

### 3. Run the AI Service
```bash
python main.py
# Or with uvicorn directly:
uvicorn main:app --reload --port 8000
```

### 4. Interactive API Documentation
Open your browser at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Automated Tests

Run the comprehensive end-to-end test suite:
```bash
python tests/test_all_ai_endpoints.py
# Or using pytest:
pytest tests/test_all_ai_endpoints.py -v
```

---

## 📡 API Endpoints Overview

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/ai/health` | `GET` | Service health status and active intelligence engine mode |
| `/api/ai/catalog` | `GET` | Platform reference dishes, macros, and allergens |
| `/api/ai/concierge` | `POST` | Conversational craving interpreter & dish recommendation |
| `/api/ai/visual-search` | `POST` | Multi-modal food recognition, macro & allergen analyzer |
| `/api/ai/smart-cart` | `POST` | Dynamic cart pairing upsells & dietary conflict alerts |
| `/api/ai/menu-copilot` | `POST` | Merchant dish descriptions, tags, and pricing benchmarks |
| `/api/ai/review-sentiment` | `POST` | Aspect-based sentiment analysis and auto-reply drafter |
| `/api/ai/event-dining-bundler` | `POST` | Night-out live event + dining itinerary planner |
| `/api/ai/predict-eta` | `POST` | Predictive kitchen prep and delivery ETA engine |
