# SECTION 15: COMPLETE 100+ INTERVIEW QUESTIONS & MODEL ANSWERS

## 15. 100+ Project-Specific Interview Questions & Model Answers

Every single question is tailored specifically to your codebase and architecture, complete with what the interviewer is testing, a strong conversational answer, a likely follow-up question, and a graceful fallback response.

---

### Category A: Beginner Questions (Project Fundamentals & Core Logic) [Q1 – Q25]

#### Q1: What is the main responsibility of this project?
* **What they are testing**: Ability to summarize system purpose and technical boundaries concisely.
* **Strong Answer**: *"It's an agentic travel planning engine that orchestrates live weather forecasts, Groq-accelerated LLM hotel and flight generation, and REST flight validation into an integrated itinerary, utilizing local SQLite caching to accelerate repeat queries."*
* **Likely Follow-up**: *"Why not just use a standard ChatGPT prompt with web browsing?"*
* **Response**: *"A raw prompt cannot deterministically query relational caches, fetch live weather APIs with reliable coordinates, or validate real flight routes with external REST services without hallucination risk."*
* **If You Don't Know**: *"At its core, it automates multi-source travel gathering into a single deterministic workflow."*

#### Q2: What is LangGraph and what role does it play here?
* **What they are testing**: Understanding of the core orchestration framework.
* **Strong Answer**: *"LangGraph is a library for building stateful, multi-actor applications with LLMs modeled as directed graphs. In this project, it compiles and orchestrates 7 independent nodes and manages conditional edge routing based on cache hits."*
* **Likely Follow-up**: *"How does state get passed between nodes?"*
* **Response**: *"Through a shared Pydantic `TravelState` object. Each node takes the current state as an argument and returns either the modified state or field updates."*
* **If You Don't Know**: *"It acts as the central state machine coordinating the sequence of agents."*

#### Q3: How many nodes are in your state graph?
* **What they are testing**: Intimate codebase familiarity.
* **Strong Answer**: *"There are 7 nodes: `weather`, `cache`, `live_search`, `flight_api`, `store`, `recommend_hotels`, and `recommend_flights`."*
* **Likely Follow-up**: *"What is the entry point node?"*
* **Response**: *"`weather` is the entry point, which calls Open-Meteo before transitioning to the cache check."*
* **If You Don't Know**: *"There are 7 nodes defined in `graph.py`, starting with weather and ending with flight recommendations."*

#### Q4: What model does the live search agent use?
* **What they are testing**: LLM stack knowledge.
* **Strong Answer**: *"It defaults to `qwen/qwen3.8-27b` hosted on Groq Cloud via their OpenAI-compatible endpoint."*
* **Likely Follow-up**: *"Why Groq over direct OpenAI or local models?"*
* **Response**: *"Groq's LPUs provide extreme token generation speed, producing our complex JSON payload in 1–2 seconds compared to 6–10 seconds on standard cloud GPUs."*
* **If You Don't Know**: *"We use Qwen-27B hosted on Groq for ultra-low inference latency."*

#### Q5: How is data cached in the application?
* **What they are testing**: Relational caching fundamentals.
* **Strong Answer**: *"We use a local SQLite database (`travel_cache.db`) with `accommodations` and `flights` tables. Before calling the LLM, the `cache` node queries SQLite by destination city and route."*
* **Likely Follow-up**: *"What constitutes a cache hit?"*
* **Response**: *"In `database/cache.py`, both accommodations and flights must have at least one record returned for that route."*
* **If You Don't Know**: *"We query SQLite tables; if both flights and hotels are present, it's considered a hit."*

#### Q6: What is the purpose of `state.py` in your codebase?
* **What they are testing**: Data modeling and shared memory structure.
* **Strong Answer**: *"It defines the `TravelState` Pydantic class, which acts as the unified schema and shared memory passed between all 7 nodes of the LangGraph state machine."*
* **Likely Follow-up**: *"Why use Pydantic instead of a standard Python dictionary?"*
* **Response**: *"Pydantic enforces runtime type validation, provides default values, and prevents missing attribute bugs across node boundaries."*
* **If You Don't Know**: *"It defines the data contract that all agents read from and write to."*

#### Q7: What fields are stored in `TravelState`?
* **What they are testing**: Familiarity with your data contracts.
* **Strong Answer**: *"It stores user inputs (`origin`, `destination`, `start_date`, `end_date`, `bedrooms`, `max_price_per_night`, `min_rating`, `max_flight_price`) and pipeline results (`weather_summary`, `accommodations`, `flights`, and `recommended_hotels`)."*
* **Likely Follow-up**: *"Are these fields required or optional?"*
* **Response**: *"Most are `Optional` with sensible defaults (like bedrooms=1, max_price=200, min_rating=4.0) so the graph never fails if a user leaves a field blank."*
* **If You Don't Know**: *"It holds both the user query constraints and the resulting lists of hotels and flights."*

#### Q8: How does the FastAPI backend receive requests from the user?
* **What they are testing**: REST interface fundamentals.
* **Strong Answer**: *"It exposes a `POST` endpoint at `/api/plan-trip` which accepts a JSON body validated against the `TripRequest` Pydantic model in `api.py`."*
* **Likely Follow-up**: *"Why not a `GET` endpoint with query parameters?"*
* **Response**: *"A travel query has 7+ constraint parameters, and on a cache miss it performs database write operations, making POST more semantically appropriate."*
* **If You Don't Know**: *"Requests are submitted as JSON via HTTP POST to `/api/plan-trip`."*

#### Q9: What happens if a user submits an invalid request, such as missing the destination?
* **What they are testing**: Input validation knowledge.
* **Strong Answer**: *"FastAPI's underlying Pydantic parser automatically intercepts the request before it reaches our business logic and returns an HTTP 422 Unprocessable Entity with exact field error details."*
* **Likely Follow-up**: *"Does this trigger any execution in LangGraph?"*
* **Response**: *"No, the request is rejected at the HTTP boundary, saving compute and preventing graph invocation."*
* **If You Don't Know**: *"FastAPI validates schemas automatically and rejects invalid payloads with 422."*

#### Q10: What is CORS and why is it configured in `api.py`?
* **What they are testing**: Browser security standards.
* **Strong Answer**: *"CORS (Cross-Origin Resource Sharing) is a browser security mechanism. In `api.py`, `CORSMiddleware` is configured to allow the React frontend on port 5173 to communicate with the FastAPI server on port 8000."*
* **Likely Follow-up**: *"Why is `allow_origins=['*']` dangerous in production?"*
* **Response**: *"Wildcard origins allow any malicious third-party site to issue authenticated requests to your API from a victim's browser; in production it should be restricted to our frontend domain."*
* **If You Don't Know**: *"It allows the Vite frontend and FastAPI backend running on different ports to communicate."*

#### Q11: What frontend technology did you choose and why?
* **What they are testing**: UI stack rationale.
* **Strong Answer**: *"React 19 with Vite. Vite provides fast HMR (Hot Module Replacement) and efficient bundling, while React provides component-based state management for dynamic result rendering and instant client-side filtering."*
* **Likely Follow-up**: *"Did you use any CSS UI library like Tailwind or Bootstrap?"*
* **Response**: *"No, I used custom Vanilla CSS in `index.css` with CSS custom properties (variables) to implement modern glassmorphism and animations without bundle overhead."*
* **If You Don't Know**: *"I used React and Vite for fast development and reactive UI state."*

#### Q12: How does the Open-Meteo API work in `weather_agent.py`?
* **What they are testing**: Third-party API integration.
* **Strong Answer**: *"It operates in two stages: first, it calls Open-Meteo's geocoding API to resolve the destination city name into latitude and longitude coordinates. Second, it calls the forecast API to retrieve daily maximum and minimum temperatures."*
* **Likely Follow-up**: *"Does Open-Meteo require an API key?"*
* **Response**: *"No, Open-Meteo provides free, keyless access for open-source and non-commercial tiers."*
* **If You Don't Know**: *"It geocodes the city name to coordinates, then fetches the temperature forecast."*

#### Q13: What does the `store_results` node do?
* **What they are testing**: Data persistence flow.
* **Strong Answer**: *"It persists freshly generated accommodations and flights into the SQLite database. It is only triggered on cache misses so that subsequent repeat searches can hit the cache."*
* **Likely Follow-up**: *"Does it execute on a cache hit?"*
* **Response**: *"No, on a cache hit, `route_cache` bypasses `store` and jumps directly to recommendation nodes."*
* **If You Don't Know**: *"It saves newly fetched hotels and flights into SQLite for future cache hits."*

#### Q14: How does `recommend_hotels` rank accommodations?
* **What they are testing**: Algorithmic sorting logic.
* **Strong Answer**: *"It sorts hotels using a compound tuple key: `(-rating, price)`. This prioritizes the highest user ratings first, and breaks ties with lower prices."*
* **Likely Follow-up**: *"How many hotels does it return to the user?"*
* **Response**: *"It slices the top 10 hotels from the sorted list and generates Google Search URLs for each."*
* **If You Don't Know**: *"It sorts primarily by rating descending, and secondarily by price ascending."*

#### Q15: How does `recommend_flights` rank flight options?
* **What they are testing**: Sorting and edge-case handling.
* **Strong Answer**: *"It sorts flights by ascending price. If a flight has a missing or non-numeric price, it assigns a high penalty value (`9,999,999.0`) so it moves to the bottom, then keeps the top 8 cheapest."*
* **Likely Follow-up**: *"Why top 8?"*
* **Response**: *"To avoid cognitive overload on the user and keep the UI clean while providing sufficient choice."*
* **If You Don't Know**: *"It sorts flights cheapest first and caps the output at 8 options."*

#### Q16: How are environment variables managed in this project?
* **What they are testing**: Configuration management.
* **Strong Answer**: *"They are stored in a root `.env` file and loaded into Python's runtime environment using `python-dotenv` via `load_dotenv()` at startup in `api.py` and `main.py`."*
* **Likely Follow-up**: *"What keys are stored in `.env`?"*
* **Response**: *"`GROQ_API_KEY` for LLM inference and optionally `AVIATIONSTACK_API_KEY` for live flight data."*
* **If You Don't Know**: *"We use a `.env` file with `python-dotenv` to keep API keys out of source code."*

#### Q17: What is the entry point file for running the backend API?
* **What they are testing**: Project operation.
* **Strong Answer**: *"`api.py` is the entry point, executed via Uvicorn with `uvicorn api:app --reload` or `python api.py`."*
* **Likely Follow-up**: *"Can the system run without the web server?"*
* **Response**: *"Yes, `main.py` provides an interactive terminal CLI interface that invokes the exact same LangGraph pipeline directly."*
* **If You Don't Know**: *"`api.py` starts the FastAPI server, while `main.py` runs the CLI."*

#### Q18: What is the purpose of `database/sqlite_client.py`?
* **What they are testing**: Database connection architecture.
* **Strong Answer**: *"It acts as the database connection factory. Its `get_conn()` function opens a connection to `travel_cache.db`, configures `conn.row_factory = sqlite3.Row`, and runs `CREATE TABLE IF NOT EXISTS` for both tables."*
* **Likely Follow-up**: *"Why set `row_factory = sqlite3.Row`?"*
* **Response**: *"It allows database cursor rows to be accessed by column name like dictionaries instead of just positional tuple indices."*
* **If You Don't Know**: *"It initializes the SQLite connection and ensures tables exist."*

#### Q19: What are the two tables created in `travel_cache.db`?
* **What they are testing**: Schema awareness.
* **Strong Answer**: *"`accommodations` (storing name, city, country, bedrooms, price_per_night, rating, url) and `flights` (storing airline, origin, destination, depart/arrive times, price, url)."*
* **Likely Follow-up**: *"Do these tables have primary keys?"*
* **Response**: *"Yes, both tables use `id INTEGER PRIMARY KEY AUTOINCREMENT`."*
* **If You Don't Know**: *"`accommodations` and `flights`."*

#### Q20: What is the purpose of `_google_flights_url()` in `flight_api_agent.py`?
* **What they are testing**: Practical integration knowledge.
* **Strong Answer**: *"It dynamically constructs a pre-filtered Google Flights URL with encoded query parameters (`Flights from {origin} to {dest} on {date}`) using `urllib.parse.quote_plus`."*
* **Likely Follow-up**: *"Why generate a Google Flights link instead of direct airline booking links?"*
* **Response**: *"Direct booking deep links require complex airline affiliate APIs; Google Flights links provide reliable, interactive booking without authentication."*
* **If You Don't Know**: *"It creates clickable Google Flights links for each route."*

#### Q21: What is the purpose of `_google_hotel_search_url()` in `recommend_agent.py`?
* **What they are testing**: URL generation logic.
* **Strong Answer**: *"It constructs a Google Search URL combining the hotel name, city, and country so users can click directly from the UI to verify amenities, photos, and reviews."*
* **Likely Follow-up**: *"Why not use direct hotel booking links?"*
* **Response**: *"LLM-generated hotels approximate realistic properties; a Google Search link guarantees the user lands on verified information even if the exact URL wasn't provided."*
* **If You Don't Know**: *"It builds a Google search link for each hotel name and city."*

#### Q22: How does the client trigger a search?
* **What they are testing**: Frontend data submission.
* **Strong Answer**: *"The user fills out the form in `App.jsx` and clicks 'Generate Trip Plan'. The `handleSubmit` function intercepts the form submission, prevents page reload (`e.preventDefault()`), and sends a fetch request to `/api/plan-trip`."*
* **Likely Follow-up**: *"What visual feedback is shown while the search runs?"*
* **Response**: *"The submit button disables and shows a spinning CSS loader with the text 'AI is Planning...'."*
* **If You Don't Know**: *"A standard form submit event triggers an asynchronous fetch call to the backend."*

#### Q23: What does the `/health` endpoint in `api.py` return?
* **What they are testing**: API observability standards.
* **Strong Answer**: *"It returns a simple JSON object: `{'status': 'ok'}` with HTTP status code 200."*
* **Likely Follow-up**: *"Why is a health endpoint necessary?"*
* **Response**: *"Container orchestrators like Kubernetes and cloud load balancers use it to probe whether the pod is alive and ready to accept traffic."*
* **If You Don't Know**: *"It returns `{'status': 'ok'}` for monitoring and uptime checks."*

#### Q24: What is the default temperature used in `search_agent.py` and why?
* **What they are testing**: LLM hyperparameter tuning.
* **Strong Answer**: *"A low temperature of `0.3`. This reduces sampling randomness, keeping the LLM focused on strictly adhering to the JSON schema and user constraints rather than hallucinating unstructured creative prose."*
* **Likely Follow-up**: *"What would happen if temperature was set to 1.2?"*
* **Response**: *"Output variance would spike, leading to frequent JSON syntax errors, missing keys, and hallucinated price formats."*
* **If You Don't Know**: *"It's set to 0.3 to enforce deterministic, structured JSON output."*

#### Q25: How does the UI handle search errors?
* **What they are testing**: Frontend resilience.
* **Strong Answer**: *"In `App.jsx`, error states are caught in a `try...catch` block, stored in the `error` state variable, and rendered as a red-bordered glassmorphic alert card informing the user."*
* **Likely Follow-up**: *"What happens if the backend server is down?"*
* **Response**: *"The fetch promise rejects, triggering the catch block with 'Failed to fetch travel plan. Please check your backend.'."*
* **If You Don't Know**: *"Errors are caught in state and displayed in an alert card."*

---
