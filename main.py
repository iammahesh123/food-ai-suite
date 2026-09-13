"""Food AI Suite - Pure AI Service Application Entrypoint."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers.ai_router import router as ai_router

app = FastAPI(
    title="Food AI Suite - Pure AI Intelligence Microservice",
    description="""
## Pure Backend AI Capabilities for Food Delivery & Dining Ecosystem

This service provides 7 end-to-end AI capabilities:
1. **TasteBot AI Concierge** (`/api/ai/concierge`): Natural language craving interpreter & dish recommendation.
2. **Snap & Crave Visual Search** (`/api/ai/visual-search`): Multi-modal food recognition, macro & allergen analyzer.
3. **Smart Cart & Safety Guard** (`/api/ai/smart-cart`): Dynamic meal pairing upsells & dietary conflict detection.
4. **Merchant Menu Copilot** (`/api/ai/menu-copilot`): Gourmet descriptions, culinary SEO tags, and price benchmarks.
5. **Customer Review Sentiment** (`/api/ai/review-sentiment`): Aspect-based sentiment analysis and auto-reply drafter.
6. **Night-Out Event Bundler** (`/api/ai/event-dining-bundler`): Live event + dining timeline planner.
7. **Predictive ETA Engine** (`/api/ai/predict-eta`): Multi-factor kitchen queue and logistics ETA predictor.

Explore and test all endpoints interactively below!
    """,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for flexible integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount AI Router
app.include_router(ai_router)

@app.get("/", summary="Root index")
def root_index():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs",
        "endpoints": [
            "/api/ai/health",
            "/api/ai/catalog",
            "/api/ai/concierge",
            "/api/ai/visual-search",
            "/api/ai/smart-cart",
            "/api/ai/menu-copilot",
            "/api/ai/review-sentiment",
            "/api/ai/event-dining-bundler",
            "/api/ai/predict-eta"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=(settings.ENVIRONMENT == "development")
    )
