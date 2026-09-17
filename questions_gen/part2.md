### Category B: Intermediate Questions (Architecture, Implementation & Decisions) [Q26 – Q50]

#### Q26: Why is `plan_trip` defined with `def` instead of `async def` in `api.py`?
* **What they are testing**: Deep understanding of FastAPI and Python asyncio event loops.
* **Strong Answer**: *"Because LangGraph's `graph.invoke()` and our internal agents use synchronous I/O (`requests.get` and `sqlite3`). In FastAPI, an `async def` handler runs directly on the main event loop; calling blocking I/O there blocks all incoming traffic. Defining it as `def` instructs FastAPI to offload execution to an AnyIO worker threadpool."*
* **Likely Follow-up**: *"How would you refactor it to be fully async?"*
* **Response**: *"Replace `requests` with `httpx.AsyncClient`, use `aiosqlite` for database queries, change the handler to `async def`, and invoke the graph with `await graph.ainvoke()`."*
* **If You Don't Know**: *"Because it contains blocking synchronous calls, and FastAPI runs `def` routes in a threadpool."*

#### Q27: Walk me through the conditional edge `route_cache` in `graph.py`.
* **What they are testing**: LangGraph graph construction and routing semantics.
* **Strong Answer**: *"In `graph.py`, `route_cache` inspects the state. If both accommodations and flights are populated from the cache node, it returns the string `'recommend_hotels'`, bypassing `live_search`, `flight_api`, and `store`. If empty, it returns `'live_search'`."*
* **Likely Follow-up**: *"What happens if only hotels are cached, but flights are empty?"*
* **Response**: *"The check `if accommodations and flights:` evaluates to False, so it routes to `live_search` to ensure the user gets complete travel recommendations."*
* **If You Don't Know**: *"It checks if cached data exists; if yes, it skips to recommendations; if no, it runs the live search."*

#### Q28: How do you handle non-numeric or missing flight prices during sorting?
* **What they are testing**: Defensive coding practices.
* **Strong Answer**: *"In `agents/flights_agent.py`, the `price_value` helper function checks if price is `None` or non-numeric and assigns a penalty float of `9,999,999.0`. This ensures unpriced flights sort cleanly to the bottom rather than raising a `TypeError` during list sorting."*
* **Likely Follow-up**: *"Why not filter unpriced flights out entirely?"*
* **Response**: *"Sometimes flight routes are valid even if real-time pricing isn't available from the API; showing the flight with a link is better than showing zero options."*
* **If You Don't Know**: *"We assign a massive penalty number so unpriced flights appear last."*

#### Q29: How does the flight API agent merge AviationStack data with LLM data?
* **What they are testing**: Data enrichment and smart merge algorithms.
* **Strong Answer**: *"It implements a smart merge: it uses AviationStack to discover verified passenger airlines and generate valid Google Flights search links. If LLM flights exist, it enriches their URLs while preserving the estimated prices; if LLM flights were empty, it falls back to using the API flights directly."*
* **Likely Follow-up**: *"Why not use AviationStack prices directly?"*
* **Response**: *"The free tier of AviationStack does not return live ticket pricing, only flight schedules and routes. The LLM provides realistic price estimates."*
* **If You Don't Know**: *"It uses AviationStack to verify airlines and links, while keeping LLM estimated prices."*

#### Q30: How does client-side star rating filtering work in React?
* **What they are testing**: Full-stack architecture and state derivation.
* **Strong Answer**: *"When the user changes the rating dropdown in React, an `onChange` handler updates component state (`minRatingFilter`). A derived variable `filteredHotels = results.recommended_hotels.filter(...)` recomputes in memory instantly without sending another HTTP request to the backend."*
* **Likely Follow-up**: *"Why not do filtering on the server?"*
* **Response**: *"The backend already returned the top-ranked hotels. Filtering in client memory takes <1ms and avoids unnecessary network latency and server load."*
* **If You Don't Know**: *"React updates a state variable and filters the existing array in memory."*

#### Q31: How do you protect against SQL injection in your database queries?
* **What they are testing**: Application security fundamentals.
* **Strong Answer**: *"All SQL queries in `database/cache.py` and `database/store_results.py` use parameterized placeholders (`?`) instead of Python string concatenation or f-strings. SQLite safely escapes parameter values, completely neutralizing SQL injection."*
* **Likely Follow-up**: *"What would the vulnerable version look like?"*
* **Response**: *"Writing `f'SELECT * FROM accommodations WHERE city = \"{state.destination}\"'` which allows attackers to inject malicious SQL via the city input."*
* **If You Don't Know**: *"By using parameterized queries with `?` placeholders."*

#### Q32: Explain the JSON sanitization logic in `agents/search_agent.py`.
* **What they are testing**: Robust LLM post-processing.
* **Strong Answer**: *"LLMs frequently output markdown fences (```` ```json ````) or invalid trailing commas (`{ 'a': 1, }`). In `search_agent.py`, we strip code block delimiters and replace `,}` with `}` and `,]` with `]` before calling `json.loads()`, drastically reducing parse failures."*
* **Likely Follow-up**: *"What if the LLM output is completely broken?"*
* **Response**: *"A blanket `try...except` catches `json.JSONDecodeError`, logs the error, and sets `accommodations = []` and `flights = []` so the pipeline degrades gracefully without crashing."*
* **If You Don't Know**: *"We clean markdown fences and trailing commas before parsing JSON."*

#### Q33: How does the system map city names to airport IATA codes?
* **What they are testing**: Data normalization techniques.
* **Strong Answer**: *"In `agents/flight_api_agent.py`, a `CITY_TO_IATA` dictionary maps major Indian and international hubs (e.g., `'Mumbai': 'BOM'`, `'Bengaluru': 'BLR'`, `'Delhi': 'DEL'`). If a city is missing from the dictionary, `_city_to_iata` defensively falls back to taking the first 3 letters uppercase."*
* **Likely Follow-up**: *"How would you improve this IATA mapping for production?"*
* **Response**: *"Use a comprehensive offline SQLite airport database or an airport lookup API like AviationStack's `/airports` endpoint."*
* **If You Don't Know**: *"We use a dictionary lookup with a 3-letter uppercase fallback."*

#### Q34: What is the purpose of `_is_passenger_airline()` in `flight_api_agent.py`?
* **What they are testing**: Domain-specific heuristic filtering.
* **Strong Answer**: *"AviationStack returns all commercial aviation flights, including cargo and freight carriers. This function checks airline names against banned substrings like 'cargo', 'freight', 'fedex', 'dhl', and 'blue dart' to prevent cargo flights from being recommended to travelers."*
* **Likely Follow-up**: *"Is this case-sensitive?"*
* **Response**: *"No, it normalizes the airline name to lowercase (`name.lower()`) before checking banned substrings."*
* **If You Don't Know**: *"It filters out cargo and courier airlines like FedEx and DHL."*

#### Q35: How does Pydantic perform type coercion in `state.py` and `api.py`?
* **What they are testing**: Pydantic data validation mechanics.
* **Strong Answer**: *"Pydantic inspects incoming dictionary values and automatically coerces types if possible—for example, converting a string `'15000'` into a float `15000.0`, or a string `'2'` into an integer `2`. If coercion is impossible (e.g., `'abc'` for price), it raises a validation error."*
* **Likely Follow-up**: *"What is the difference between `model_dump()` and `dict()` in Pydantic?"*
* **Response**: *"`model_dump()` is the modern Pydantic v2 method, while `dict()` is deprecated from Pydantic v1."*
* **If You Don't Know**: *"Pydantic automatically coerces compatible types and validates constraints."*

#### Q36: Why does the graph compile with `graph.compile()`?
* **What they are testing**: LangGraph lifecycle and compilation.
* **Strong Answer**: *"Calling `compile()` validates the graph structure (ensuring entry points, valid edges, and no dangling nodes) and returns a `CompiledStateGraph` implementing the LangChain Runnable protocol, which exposes methods like `invoke()` and `ainvoke()`."*
* **Likely Follow-up**: *"Can you modify a graph after compiling it?"*
* **Response**: *"No, the compiled graph is immutable; changes require rebuilding or recompiling."*
* **If You Don't Know**: *"It validates graph integrity and turns it into an executable runnable."*

#### Q37: What is the significance of the `vector_search.py` file in `database/`?
* **What they are testing**: Honesty about unfinished or planned features.
* **Strong Answer**: *"It is currently an empty placeholder file (0 bytes). In the upstream prototype, it was envisioned for vector-based semantic search. In our current implementation, we use relational SQL caching instead."*
* **Likely Follow-up**: *"How would you implement it if asked?"*
* **Response**: *"Generate vector embeddings for hotel descriptions using OpenAI or HuggingFace models, store them in SQLite using `sqlite-vec` or in pgvector, and query them using cosine similarity for 'vibe' searches."*
* **If You Don't Know**: *"It is an empty placeholder for future semantic vector search."*

#### Q38: What role does `reference_repo` play in your workspace?
* **What they are testing**: Project heritage and honesty.
* **Strong Answer**: *"It contains the cloned upstream prototype by Pavan Belagatti that originally used SingleStore. I migrated the codebase to use local SQLite, integrated Groq Qwen-27B, built the FastAPI backend, and designed the React 19 frontend."*
* **Likely Follow-up**: *"Why migrate from SingleStore to SQLite?"*
* **Response**: *"SingleStore required paid cloud database credentials or heavy Docker infrastructure; SQLite made the project completely self-contained, reproducible, and portable."*
* **If You Don't Know**: *"It's the upstream prototype from which I built the SQLite and React versions."*

#### Q39: How does the glassmorphism UI work in `frontend/src/index.css`?
* **What they are testing**: CSS and modern frontend styling.
* **Strong Answer**: *"It uses CSS `backdrop-filter: blur(16px)` combined with semi-transparent background colors (`rgba(255, 255, 255, 0.05)`), subtle borders (`1px solid rgba(255, 255, 255, 0.1)`), and box shadows to achieve a translucent frosted-glass aesthetic."*
* **Likely Follow-up**: *"What browser compatibility issues exist with `backdrop-filter`?"*
* **Response**: *"Older browsers or Safari require vendor prefix `-webkit-backdrop-filter`, and low-powered mobile devices can experience minor GPU overhead during repaints."*
* **If You Don't Know**: *"Using semi-transparent backgrounds and `backdrop-filter: blur()`."*

#### Q40: What is the difference between `main.py` and `api.py`?
* **What they are testing**: Architecture separation.
* **Strong Answer**: *"`main.py` is a CLI tool that uses `input()` prompts to run the graph and print results to the console. `api.py` is an HTTP web service exposing the graph via a REST API to web clients."*
* **Likely Follow-up**: *"Do they share the same graph logic?"*
* **Response**: *"Yes, both import and call `build_graph()` from `graph.py` and pass `TravelState` instances, demonstrating clean separation of interface and business logic."*
* **If You Don't Know**: *"`main.py` is for terminal CLI usage; `api.py` powers the web app."*

#### Q41: How does `agents/cache_agent.py` differ from `database/cache.py`?
* **What they are testing**: Codebase cleanup awareness.
* **Strong Answer**: *"`agents/cache_agent.py` is a legacy file from the SingleStore prototype that imports `singlestore_client`. The active cache logic used by our graph is in `database/cache.py`, which uses SQLite."*
* **Likely Follow-up**: *"Why keep the old file?"*
* **Response**: *"It was retained during initial migration for reference, but in a production cleanup it should be deleted to prevent developer confusion."*
* **If You Don't Know**: *"One is the legacy SingleStore agent; the other is the active SQLite cache."*

#### Q42: What happens if a user enters a negative price or negative bedroom count?
* **What they are testing**: Defensive input boundary testing.
* **Strong Answer**: *"In `App.jsx`, HTML input elements enforce `min='1'` for bedrooms and `min='100'` for price. In `api.py`, default values exist, but we could add Pydantic `Field(gt=0)` constraints to reject negative numbers at the API level."*
* **Likely Follow-up**: *"Why is client-side validation not enough?"*
* **Response**: *"Because an attacker can bypass the React frontend using Postman or curl and submit negative values directly to the API."*
* **If You Don't Know**: *"HTML inputs prevent it in the UI, but API-level Pydantic validators should also enforce it."*

#### Q43: How does the system handle city casing (e.g., 'mumbai' vs 'Mumbai')?
* **What they are testing**: String normalization and database indexing.
* **Strong Answer**: *"In `database/cache.py`, SQL uses `WHERE LOWER(city) = LOWER(?)`, ensuring case-insensitive matching regardless of user input casing."*
* **Likely Follow-up**: *"Is `LOWER(city) = LOWER(?)` performant on large tables?"*
* **Response**: *"No, it causes a full table scan. In production, we should index `city COLLATE NOCASE` and query directly."*
* **If You Don't Know**: *"By applying `LOWER()` to both the database column and the input parameter."*

#### Q44: What is the role of `vite.config.js` in the frontend?
* **What they are testing**: Modern JavaScript build tooling.
* **Strong Answer**: *"It configures Vite, enabling the `@vitejs/plugin-react` plugin for Fast Refresh and JSX compilation, and sets up server port and proxy options if needed."*
* **Likely Follow-up**: *"How does Vite compare to Create React App (Webpack)?"*
* **Response**: *"Vite uses native ES modules (ESM) in development and esbuild for pre-bundling, starting dev servers in milliseconds compared to Webpack's slow bundle compilation."*
* **If You Don't Know**: *"It configures plugins and build settings for the React application in Vite."*

#### Q45: How does Groq's API compatibility with OpenAI work?
* **What they are testing**: SDK and API abstraction knowledge.
* **Strong Answer**: *"Groq implements the exact same REST API schema as OpenAI's `/v1/chat/completions`. In `search_agent.py`, we use the standard `openai.OpenAI` SDK and simply override `base_url='https://api.groq.com/openai/v1'`."*
* **Likely Follow-up**: *"What benefit does this provide?"*
* **Response**: *"Zero SDK lock-in: we can swap back to OpenAI, Anthropic, or local vLLM by changing two environment variables without rewriting agent code."*
* **If You Don't Know**: *"Groq mirrors OpenAI's API format, so the official OpenAI SDK works directly."*

#### Q46: What happens if `GROQ_API_KEY` is not set?
* **What they are testing**: Environment failure behavior.
* **Strong Answer**: *"In `agents/search_agent.py`, `get_groq_client()` logs a warning `[WARNING] GROQ_API_KEY is not set in environment!` and falls back to `'missing_key'`, causing Groq API calls to throw an AuthenticationError caught in `live_search`."*
* **Likely Follow-up**: *"How should a production application handle missing keys at startup?"*
* **Response**: *"Fail fast: raise a `RuntimeError` during startup in `api.py` so the server refuses to start with invalid configuration."*
* **If You Don't Know**: *"It prints a warning and API calls fail with an authentication error."*

#### Q47: How does `App.jsx` prevent multiple simultaneous submissions?
* **What they are testing**: UI state management.
* **Strong Answer**: *"When a search starts, `loading` state is set to `true`. The submit button binds `disabled={loading}`, preventing the user from triggering concurrent duplicate requests."*
* **Likely Follow-up**: *"What happens if the request takes 30 seconds?"*
* **Response**: *"The user is blocked from submitting again until the request resolves or fails, protecting the backend from being hammered."*
* **If You Don't Know**: *"By disabling the submit button while `loading` is true."*

#### Q48: What is the purpose of `oxlint` in `frontend/package.json`?
* **What they are testing**: Developer tooling familiarity.
* **Strong Answer**: *"`oxlint` is an ultra-fast Rust-based JavaScript/JSX linter designed to catch common errors and syntax bugs 50–100x faster than ESLint."*
* **Likely Follow-up**: *"Does it replace ESLint entirely?"*
* **Response**: *"For common syntax and security checks, yes; but complex custom AST rules still sometimes use ESLint alongside it."*
* **If You Don't Know**: *"It's a fast Rust-based linter for JavaScript and React code."*

#### Q49: What is the data type of `price` in `state.py`?
* **What they are testing**: Schema detail awareness.
* **Strong Answer**: *"In `TravelState`, budget constraints like `max_price_per_night` and `max_flight_price` are `Optional[float]`, accommodating decimal currency values."*
* **Likely Follow-up**: *"Why not use `Decimal` for financial calculations?"*
* **Response**: *"For display and recommendation estimates, `float` is sufficient; but in production payment transactions, Python's `decimal.Decimal` is required to avoid IEEE-754 floating point inaccuracies."*
* **If You Don't Know**: *"They are stored as floating point numbers (`float`)."*

#### Q50: How does `graph.invoke()` execute compared to `graph.stream()`?
* **What they are testing**: LangGraph execution modes.
* **Strong Answer**: *"`invoke()` runs the entire graph to completion synchronously and returns only the final accumulated state. `stream()` yields state updates after each node executes, enabling real-time UI streaming."*
* **Likely Follow-up**: *"Why did you use `invoke()` instead of `stream()`?"*
* **Response**: *"Because our REST endpoint returns a single consolidated JSON response. In a future iteration, we could use `stream()` with Server-Sent Events (SSE) to show progress as each node completes."*
* **If You Don't Know**: *"`invoke` runs the entire graph at once, while `stream` emits updates node-by-node."*

---
