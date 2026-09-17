from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from graph import build_graph
from state import TravelState

app = FastAPI(title="Travel Agent API")

# Setup CORS for the Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TripRequest(BaseModel):
    origin: str
    destination: str
    start_date: str
    end_date: str
    bedrooms: int = 1
    max_price_per_night: float = 200.0
    min_rating: float = 4.0

@app.post("/api/plan-trip")
def plan_trip(request: TripRequest):
    graph = build_graph()
    
    initial_state = TravelState(
        origin=request.origin,
        destination=request.destination,
        start_date=request.start_date,
        end_date=request.end_date,
        bedrooms=request.bedrooms,
        max_price_per_night=request.max_price_per_night,
        min_rating=request.min_rating,
    )

    try:
        final_state = graph.invoke(initial_state)
        
        # Normalize to dict if not already
        if isinstance(final_state, TravelState):
            final_state = final_state.model_dump()
            
        return {
            "weather_summary": final_state.get("weather_summary"),
            "recommended_hotels": final_state.get("recommended_hotels", []),
            "flights": final_state.get("flights", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}
