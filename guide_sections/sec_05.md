# SECTION 5: END-TO-END EXECUTION FLOWS

## 4. End-to-End Execution Flows

Understanding the exact step-by-step lifecycle of user requests through files, functions, and state mutations is essential for surviving technical walkthroughs.

---

### Flow 1: Cold Search Execution (Cache Miss Lifecycle)

```text
User Submits Form -> React Frontend -> FastAPI POST /api/plan-trip -> LangGraph Compiled Graph
  -> weather node (Open-Meteo) -> cache node (Miss) -> route_cache() conditional branch
  -> live_search node (Groq Qwen-27B) -> flight_api node (AviationStack) -> store node (SQLite INSERT)
  -> recommend_hotels node (Sort & Links) -> recommend_flights node (Sort) -> JSON Response -> React Render
```

1. **Trigger**: User inputs origin `"BLR"`, destination `"Mumbai"`, dates, bedrooms `1`, budget `15000` in the React UI and clicks `"Generate Trip Plan ✈️"`.
2. **Client Dispatch**: [`frontend/src/App.jsx:L27`](file:///d:/Programming/sde_projects/travelagent/frontend/src/App.jsx#L27) `handleSubmit()` sets `loading = true`, resets `error` and `results`, and sends an HTTP POST with JSON body to `http://localhost:8000/api/plan-trip`.
3. **API Reception & Validation**: [`api.py:L31`](file:///d:/Programming/sde_projects/travelagent/api.py#L31) `plan_trip(request: TripRequest)` receives payload. FastAPI and Pydantic validate that `origin`, `destination`, `start_date`, and `end_date` are strings, and numeric fields match bounds.
4. **State Initialization & Graph Compilation**:
   * An initial `TravelState` instance is created ([`state.py:L4`](file:///d:/Programming/sde_projects/travelagent/state.py#L4)) populated with user criteria.
   * `build_graph()` in [`graph.py:L29`](file:///d:/Programming/sde_projects/travelagent/graph.py#L29) compiles the `StateGraph`.
   * Execution begins via `final_state = graph.invoke(initial_state)` ([`api.py:L46`](file:///d:/Programming/sde_projects/travelagent/api.py#L46)).
5. **Node 1: Weather Execution**:
   * [`agents/weather_agent.py:L3`](file:///d:/Programming/sde_projects/travelagent/agents/weather_agent.py#L3) `fetch_weather(state)` calls Open-Meteo geocoding API to resolve `"Mumbai"` to latitude `19.0760` and longitude `72.8777`.
   * Calls Open-Meteo forecast API for daily min and max 2m temperatures.
   * Mutates `state.weather_summary = "Temperature ranges between 24.2°C and 32.5°C."`.
6. **Node 2: Cache Inspection**:
   * [`database/cache.py:L3`](file:///d:/Programming/sde_projects/travelagent/database/cache.py#L3) `check_cache(state)` queries SQLite for hotels where `LOWER(city) = LOWER('Mumbai')` and flights where `origin = 'BLR' AND destination = 'Mumbai'`.
   * Since this is a cold query, `hotels` or `flights` returns 0 rows.
   * Function returns `None`.
7. **Conditional Routing**:
   * [`graph.py:L13`](file:///d:/Programming/sde_projects/travelagent/graph.py#L13) `route_cache(state)` checks if accommodations and flights exist in state. Because they are empty, it returns the string `"live_search"`.
8. **Node 3: Live Search (LLM Orchestration)**:
   * [`agents/search_agent.py:L16`](file:///d:/Programming/sde_projects/travelagent/agents/search_agent.py#L16) `live_search(state)` formats system prompt with strict JSON output schema and user prompt containing constraints.
   * Calls Groq OpenAI-compatible client endpoint (`https://api.groq.com/openai/v1`) requesting model `qwen/qwen3.8-27b` at `temperature=0.3`.
   * Raw text output is stripped of markdown fences (```` ```json ````) and sanitized for trailing commas.
   * `json.loads(cleaned)` parses the payload into lists.
   * Mutates `state.accommodations` and `state.flights`.
9. **Node 4: Flight Enrichment (API Smart Merge)**:
   * [`agents/flight_api_agent.py:L57`](file:///d:/Programming/sde_projects/travelagent/agents/flight_api_agent.py#L57) `fetch_flights_from_api(state)` converts destination to IATA `"BOM"`.
   * Checks `AVIATIONSTACK_API_KEY`. If key is present and valid, calls `http://api.aviationstack.com/v1/flights`.
   * Filters out cargo carriers via `_is_passenger_airline()`, generates Google Flights search URLs, and overwrites flight URLs in `state.flights` while preserving LLM-generated prices.
10. **Node 5: Persistence on Cache Miss**:
    * [`database/store_results.py:L3`](file:///d:/Programming/sde_projects/travelagent/database/store_results.py#L3) `store_results(state)` opens SQLite connection.
    * Executes parameterized batch `INSERT` statements into `accommodations` and `flights` tables.
    * Calls `conn.commit()` and `conn.close()`.
11. **Node 6: Hotel Recommendation & Search URL Generation**:
    * [`agents/recommend_agent.py:L16`](file:///d:/Programming/sde_projects/travelagent/agents/recommend_agent.py#L16) `recommend_hotels(state)` sorts `state.accommodations` using compound key `(-rating, price)` so highest-rated, lowest-priced hotels appear first.
    * Takes top 10 hotels, attaches real Google Search URLs (`https://www.google.com/search?q=Hotel+Name+City`), and writes to `state.recommended_hotels`.
12. **Node 7: Flight Ranking**:
    * [`agents/flights_agent.py:L3`](file:///d:/Programming/sde_projects/travelagent/agents/flights_agent.py#L3) `recommend_flights(state)` sorts flights by ascending price. Non-numeric or missing prices are given a penalty value of `9,999,999.0` to sink to the bottom.
    * Slices top 8 cheapest flights into `state.flights`.
    * Graph reaches `END`.
13. **Response Packaging**:
    * [`api.py:L50-56`](file:///d:/Programming/sde_projects/travelagent/api.py#L50-L56) dumps `TravelState` to dict and returns HTTP 200 with keys `weather_summary`, `recommended_hotels`, and `flights`.
14. **Client Render**:
    * [`frontend/src/App.jsx:L48-52`](file:///d:/Programming/sde_projects/travelagent/frontend/src/App.jsx#L48-L52) sets `results = data`, disables loading spinner, and renders weather badge, hotel cards, and flight cards.

---

### Flow 2: Warm Search Execution (Cache Hit Lifecycle)

```text
User Submits Repeat Form -> React Frontend -> FastAPI POST /api/plan-trip -> LangGraph
  -> weather node (Open-Meteo) -> cache node (Hit: reads SQLite) -> route_cache() conditional branch
  -> [BYPASSES live_search, flight_api, store]
  -> recommend_hotels node -> recommend_flights node -> JSON Response -> React Render
```

1. **Difference from Cold Flow**: A user submits the same route (`origin="BLR"`, `destination="Mumbai"`).
2. **Cache Inspection**:
   * [`database/cache.py:L8-43`](file:///d:/Programming/sde_projects/travelagent/database/cache.py#L8-L43) queries SQLite for existing rows in `accommodations` and `flights`.
   * It finds rows previously stored by Flow 1.
   * Mutates `state.accommodations = hotels` and `state.flights = flights` and returns updated `state`.
3. **Deterministic Branching**:
   * [`graph.py:L24`](file:///d:/Programming/sde_projects/travelagent/graph.py#L24) in `route_cache(state)` evaluates:
     ```python
     if accommodations and flights:
         return "recommend_hotels"
     ```
   * The graph skips `live_search`, `flight_api`, and `store` entirely.
4. **Execution Latency Impact**: Eliminating the Groq LLM network roundtrip (~2.5–3.0s) and AviationStack API call (~500ms) drops total server processing time to sub-150ms.

---

### Flow 3: Client-Side Star Rating Filtering

```text
User Changes Rating Dropdown -> React onChange Handler -> setMinRatingFilter()
  -> React Re-renders -> in-memory Array Filter -> DOM Updates (<1ms, No Network Request)
```

1. **Trigger**: After search results load, the user selects `"4+ Stars"` from the "Filter by Rating" dropdown in the UI.
2. **State Transition**: [`frontend/src/App.jsx:L140`](file:///d:/Programming/sde_projects/travelagent/frontend/src/App.jsx#L140) executes:
   ```javascript
   onChange={(e) => setMinRatingFilter(Number(e.target.value))}
   ```
   React updates `minRatingFilter` state from `0` to `4`.
3. **Client-Side Evaluation**:
   * [`frontend/src/App.jsx:L56`](file:///d:/Programming/sde_projects/travelagent/frontend/src/App.jsx#L56) re-computes `filteredHotels`:
     ```javascript
     const filteredHotels = results?.recommended_hotels?.filter(hotel => hotel.rating >= minRatingFilter) || [];
     ```
4. **Zero Network Latency**: No HTTP request is sent to `/api/plan-trip`. The filtering executes purely in JavaScript memory over the 10 hotel objects in <1ms, updating the virtual DOM instantly.

---

### Flow 4: Weather API Geocoding & Network Failure Fallback

```text
weather node -> Open-Meteo Geocoding Request Fails -> except block catches error
  -> Lat/Lon hardcoded fallback (Mumbai) -> Open-Meteo Forecast Fails -> except block catches error
  -> state.weather_summary = "Weather unavailable." -> Pipeline Continues Smoothly
```

1. **Trigger**: User inputs a misspelled city or Open-Meteo experiences network timeout/downtime.
2. **Geocoding Exception Catch**:
   * In [`agents/weather_agent.py:L7-17`](file:///d:/Programming/sde_projects/travelagent/agents/weather_agent.py#L7-L17), the call `requests.get("https://geocoding-api.open-meteo.com/...")` throws an HTTP error or KeyError (`results` list empty).
   * The `except:` block catches the exception and falls back to default coordinates:
     ```python
     lat, lon = 19.0760, 72.8777 # Mumbai coordinates
     ```
3. **Forecast Exception Catch**:
   * In [`agents/weather_agent.py:L26-36`](file:///d:/Programming/sde_projects/travelagent/agents/weather_agent.py#L26-L36), if the forecast endpoint also fails, the `except:` block sets:
     ```python
     state.weather_summary = "Weather unavailable."
     ```
4. **Pipeline Integrity**: The function returns `state` safely without bubbling an exception up to FastAPI. LangGraph proceeds to the `cache` node uninterrupted.

---

### Flow 5: AviationStack API Outage / Missing Key Graceful Degradation

```text
flight_api node -> Check AVIATIONSTACK_API_KEY -> Key is missing / placeholder / API times out
  -> Warning logged -> Return state with untouched LLM flights -> Graph proceeds to store node
```

1. **Trigger**: Either `AVIATIONSTACK_API_KEY` is not configured in `.env` (or has default placeholder value `"your-aviationstack-key"`), or the remote API returns an HTTP 500/timeout.
2. **Defensive Check**:
   * In [`agents/flight_api_agent.py:L72-75`](file:///d:/Programming/sde_projects/travelagent/agents/flight_api_agent.py#L72-L75):
     ```python
     api_key = os.getenv("AVIATIONSTACK_API_KEY", "").strip()
     if not api_key or api_key in ["your-aviationstack-key", "your_optional_aviationstack_key_here"]:
         print("[INFO] AVIATIONSTACK_API_KEY not set or placeholder; using LLM generated flights.")
         return state
     ```
3. **Runtime Network Exception**:
   * If an API key is provided but the HTTP request fails at runtime ([`agents/flight_api_agent.py:L160-163`](file:///d:/Programming/sde_projects/travelagent/agents/flight_api_agent.py#L160-L163)):
     ```python
     except Exception as e:
         print("[WARNING] Error calling AviationStack:", str(e))
         return state
     ```
4. **Outcome**: The graph does not abort. It retains the synthetic flights generated by Groq in `state.flights` and transitions to `store`.

---
