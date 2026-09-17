# SECTION 4: CODEBASE MAP & KEY FILES

## 3. Codebase Map & Critical Files

### Repository Directory Map

```text
travelagent/
├── .env                              # Environment variables (GROQ_API_KEY, AVIATIONSTACK_API_KEY)
├── api.py                            # FastAPI entry point, CORS, Pydantic schemas, HTTP routing
├── graph.py                          # LangGraph state machine definition and conditional routing logic
├── main.py                           # CLI interactive entry point for testing graph execution locally
├── state.py                          # Pydantic TravelState definition (shared graph memory model)
├── requirements.txt                  # Python dependencies (fastapi, langgraph, openai, pydantic, etc.)
├── travel_cache.db                   # SQLite relational cache file storing accommodations & flights
│
├── agents/                           # Individual workflow agent nodes
│   ├── weather_agent.py              # Open-Meteo geocoding & temperature range query node
│   ├── search_agent.py               # Groq LLM live search with JSON prompting & sanitization
│   ├── flight_api_agent.py           # AviationStack passenger flight lookup and Google Flights URL builder
│   ├── recommend_agent.py            # Hotel recommendation, rating/price tuple sorting, and search URL generation
│   ├── flights_agent.py              # Flight price sorting, invalid price handling, and top-8 selection
│   └── cache_agent.py                # Legacy SingleStore cache agent (retained from upstream prototype)
│
├── database/                         # Relational persistence & caching tier
│   ├── sqlite_client.py              # SQLite connection factory & automatic table initialization
│   ├── cache.py                      # Parameterized SQL cache queries for accommodations and flights
│   ├── store_results.py              # Batch parameterized SQL inserts on cache miss
│   └── vector_search.py              # Empty placeholder file for future vector embedding functionality
│
├── frontend/                         # Client single page application (Vite + React 19)
│   ├── index.html                    # HTML root entry point with Google Fonts (Outfit, Inter)
│   ├── package.json                  # Frontend npm dependencies (react, react-dom, vite, oxlint)
│   ├── vite.config.js                # Vite development server and build configuration
│   └── src/
│       ├── main.jsx                  # React DOM root bootstrapping
│       ├── App.jsx                   # Main React component: form inputs, API submission, and result rendering
│       ├── App.css                   # Component-specific styles
│       └── index.css                 # Global CSS design tokens, glassmorphic styles, and responsive layout
│
└── reference_repo/                   # Cloned upstream prototype repository (SingleStore-based reference)
```

---

### Top 20 Files & Functions I Must Understand

| Rank | File / Path | Key Function / Class | Purpose & Interview Importance |
| :---: | :--- | :--- | :--- |
| **1** | [`graph.py`](file:///d:/Programming/sde_projects/travelagent/graph.py) | `build_graph()` | **Critical**: Constructs the `StateGraph`, registers all 7 nodes, assigns edges, sets the entry point, and compiles the workflow into an executable runnable. |
| **2** | [`graph.py`](file:///d:/Programming/sde_projects/travelagent/graph.py) | `route_cache(state)` | **Critical**: Conditional branching function. Returns `"recommend_hotels"` if cached data exists, or `"live_search"` on a cache miss. |
| **3** | [`state.py`](file:///d:/Programming/sde_projects/travelagent/state.py) | `class TravelState(BaseModel)` | **Critical**: Type-safe shared memory model passed into and mutated by every single node in the LangGraph graph. |
| **4** | [`api.py`](file:///d:/Programming/sde_projects/travelagent/api.py) | `@app.post("/api/plan-trip")` | **Critical**: Main REST endpoint. Parses `TripRequest`, invokes `graph.invoke()`, serializes `TravelState`, and returns JSON. |
| **5** | [`agents/search_agent.py`](file:///d:/Programming/sde_projects/travelagent/agents/search_agent.py) | `live_search(state)` | **Critical**: Formulates prompt for Groq Qwen-27B, executes LLM completion at low temperature (0.3), and parses output JSON. |
| **6** | [`agents/search_agent.py`](file:///d:/Programming/sde_projects/travelagent/agents/search_agent.py) | JSON Sanitization logic (lines 98–110) | **Critical**: Strips markdown code blocks (```` ```json ````) and cleans trailing commas (`",}"` -> `"}"`) before `json.loads()`. |
| **7** | [`database/cache.py`](file:///d:/Programming/sde_projects/travelagent/database/cache.py) | `check_cache(state)` | **Critical**: Executes parameterized SQLite queries against `accommodations` and `flights`. Determines cache hit vs miss. |
| **8** | [`database/store_results.py`](file:///d:/Programming/sde_projects/travelagent/database/store_results.py) | `store_results(state)` | **Critical**: Persists freshly fetched LLM and API data into SQLite using parameterized `INSERT` statements on cache miss. |
| **9** | [`database/sqlite_client.py`](file:///d:/Programming/sde_projects/travelagent/database/sqlite_client.py) | `get_conn()` | **Critical**: Establishes SQLite database connection with `row_factory = sqlite3.Row` and creates tables idempotently. |
| **10** | [`agents/flight_api_agent.py`](file:///d:/Programming/sde_projects/travelagent/agents/flight_api_agent.py) | `fetch_flights_from_api(state)` | **High**: Smart merge algorithm that queries AviationStack for real airline carriers and enriches LLM flight data with Google Flights URLs. |
| **11** | [`agents/flight_api_agent.py`](file:///d:/Programming/sde_projects/travelagent/agents/flight_api_agent.py) | `_is_passenger_airline(name)` | **High**: Defensive filter excluding cargo and freight carriers (FedEx, DHL, Blue Dart) from flight recommendations. |
| **12** | [`agents/recommend_agent.py`](file:///d:/Programming/sde_projects/travelagent/agents/recommend_agent.py) | `recommend_hotels(state)` | **High**: Sorts accommodations using compound sorting tuple `(-rating_f, price_f)` and attaches real Google Search URLs. |
| **13** | [`agents/flights_agent.py`](file:///d:/Programming/sde_projects/travelagent/agents/flights_agent.py) | `recommend_flights(state)` | **High**: Sorts flights by ascending price, safely treats non-numeric or `None` prices as high values (`9,999,999.0`), and slices top 8. |
| **14** | [`agents/weather_agent.py`](file:///d:/Programming/sde_projects/travelagent/agents/weather_agent.py) | `fetch_weather(state)` | **High**: Resolves city coordinates via Open-Meteo geocoding and fetches daily min/max temperatures with fallback coordinates. |
| **15** | [`frontend/src/App.jsx`](file:///d:/Programming/sde_projects/travelagent/frontend/src/App.jsx) | `handleSubmit(e)` | **High**: Client-side form submit handler that POSTs trip criteria to FastAPI and updates React state with loading/error management. |
| **16** | [`frontend/src/App.jsx`](file:///d:/Programming/sde_projects/travelagent/frontend/src/App.jsx) | `filteredHotels` (line 56) | **Medium**: Pure client-side array filter (`hotel.rating >= minRatingFilter`) demonstrating in-memory UI updates without backend network hops. |
| **17** | [`api.py`](file:///d:/Programming/sde_projects/travelagent/api.py) | `class TripRequest(BaseModel)` | **Medium**: Pydantic input schema defining validated fields, data types, and default constraints for trip planning requests. |
| **18** | [`main.py`](file:///d:/Programming/sde_projects/travelagent/main.py) | `main()` | **Medium**: Command-line interface demonstrating standalone execution of the state graph without the web server. |
| **19** | [`agents/cache_agent.py`](file:///d:/Programming/sde_projects/travelagent/agents/cache_agent.py) | `cache_agent(state)` | **Supporting**: Legacy SingleStore integration code; explains origin of project migration from SingleStore to local SQLite. |
| **20** | [`database/vector_search.py`](file:///d:/Programming/sde_projects/travelagent/database/vector_search.py) | Entire File (0 bytes) | **Interview Topic**: Empty file representing planned extension for semantic/vibe hotel search using vector embeddings. |

---
