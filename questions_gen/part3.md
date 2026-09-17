### Category C: Advanced Questions (Concurrency, Reliability & Failures) [Q51 – Q75]

#### Q51: What happens if two users execute a cold search for the same route simultaneously?
* **What they are testing**: Race conditions and database concurrency.
* **Strong Answer**: *"Both requests will experience a cache miss, call Groq concurrently, and attempt to write to `travel_cache.db`. In SQLite, the second write will wait for the file lock and insert duplicate records because there is no unique constraint on the tables. In production, we would add an idempotent unique index and use a Redis distributed lock (`SETNX`) so only one worker executes the live search."*
* **Likely Follow-up**: *"What error would be thrown if the wait timeout expires?"*
* **Response**: *"`sqlite3.OperationalError: database is locked`."*
* **If You Don't Know**: *"Both might run concurrently and insert duplicate rows into the database."*

#### Q52: How do you defend against prompt injection if user inputs are passed to the LLM?
* **What they are testing**: LLM application security.
* **Strong Answer**: *"In `agents/search_agent.py`, user variables are interpolated into the user prompt. To prevent prompt injection, we should validate inputs strictly with Pydantic regex patterns, separate user inputs into distinct message roles, and use structured outputs via OpenAI's `response_format={'type': 'json_object'}` or Pydantic Function Calling."*
* **Likely Follow-up**: *"Can an attacker execute commands via the prompt?"*
* **Response**: *"Not system commands directly, but they could manipulate output JSON to return phishing links or bypass pricing constraints."*
* **If You Don't Know**: *"By validating input strings strictly and using structured output mode."*

#### Q53: If Open-Meteo geocoding fails, how does the system recover?
* **What they are testing**: Fault tolerance and fallback logic.
* **Strong Answer**: *"In `agents/weather_agent.py`, the geocoding request is wrapped in a `try...except` block that falls back to Mumbai's coordinates `(19.0760, 72.8777)`. The graph never crashes; it logs the issue and proceeds."*
* **Likely Follow-up**: *"Why default to Mumbai instead of returning an error?"*
* **Response**: *"To ensure non-blocking execution so the user still receives flight and hotel recommendations even if weather coordinates fail."*
* **If You Don't Know**: *"It catches the error and defaults to a predefined set of coordinates."*

#### Q54: What happens if an external API call hangs indefinitely?
* **What they are testing**: Timeout management.
* **Strong Answer**: *"In `flight_api_agent.py`, `requests.get()` explicitly sets `timeout=10`. In `weather_agent.py`, no timeout is currently passed, which is a vulnerability that could cause worker threads to hang indefinitely. In production, every external HTTP call must have strict connect and read timeouts (e.g., 3-5 seconds)."*
* **Likely Follow-up**: *"What is the difference between connect timeout and read timeout?"*
* **Response**: *"Connect timeout is the time to establish the TCP handshake; read timeout is the max time waiting for data packets once connected."*
* **If You Don't Know**: *"If no timeout is set, the thread hangs indefinitely; we should always configure timeouts."*

#### Q55: How would you implement a Circuit Breaker on the Groq LLM API?
* **What they are testing**: Distributed system resilience patterns.
* **Strong Answer**: *"Using a library like `pybreaker`. If Groq fails 5 times consecutively within 60 seconds, the breaker trips to 'Open' state for 30 seconds. Subsequent requests immediately fail fast or route to a secondary LLM provider without waiting on network timeouts."*
* **Likely Follow-up**: *"What are the three states of a circuit breaker?"*
* **Response**: *"'Closed' (normal operation), 'Open' (tripped, fail fast), and 'Half-Open' (testing if remote service has recovered)."*
* **If You Don't Know**: *"It stops calling a failing service after repeated errors and tests recovery periodically."*

#### Q56: What happens if the database connection fails during `store_results`?
* **What they are testing**: Exception propagation in LangGraph.
* **Strong Answer**: *"In the current codebase, `database/store_results.py` does not wrap `cur.execute()` in a `try...except`. If SQLite throws an error, the exception bubbles up through LangGraph, causing `api.py` to catch it and return an HTTP 500 error to the client."*
* **Likely Follow-up**: *"How should this be fixed?"*
* **Response**: *"Wrap persistence in a try-except block that logs the persistence failure but returns the state anyway, allowing the user to view their results even if caching fails."*
* **If You Don't Know**: *"Currently it would bubble up and cause an HTTP 500 error."*

#### Q57: How does Python's GIL affect this application?
* **What they are testing**: Python runtime concurrency internals.
* **Strong Answer**: *"The GIL (Global Interpreter Lock) prevents multiple native threads from executing Python bytecodes simultaneously. However, this application is predominantly I/O-bound (waiting on network sockets for Groq, Open-Meteo, and SQLite), during which Python releases the GIL. AnyIO worker threads can therefore handle concurrent I/O efficiently."*
* **Likely Follow-up**: *"When would the GIL become a major bottleneck?"*
* **Response**: *"If we added heavy local CPU-bound work, like running local vector embedding models or image generation in-process."*
* **If You Don't Know**: *"The GIL restricts Python to one CPU thread, but releases during I/O operations."*

#### Q58: What is the risk of holding database connections open in long-running requests?
* **What they are testing**: Resource lifecycle and connection starvation.
* **Strong Answer**: *"Holding a database connection during slow external network calls (like waiting for Groq LLM generation) starves the connection pool. Our code avoids this: `check_cache` opens and closes the connection before LLM execution, and `store_results` opens it only when saving."*
* **Likely Follow-up**: *"What pattern avoids manually opening/closing connections?"*
* **Response**: *"Using Python context managers (`with get_conn() as conn:`) which guarantee cleanup even if exceptions are raised."*
* **If You Don't Know**: *"It exhausts available connections and blocks other requests from accessing the database."*

#### Q59: How does the system guarantee idempotency on cache misses?
* **What they are testing**: Idempotency and distributed state.
* **Strong Answer**: *"It currently does not guarantee strict idempotency. Repeated identical cache-miss requests insert duplicate rows into SQLite. To make it idempotent, we should compute a SHA-256 hash of the normalized request parameters and use it as a unique key for deduplication."*
* **Likely Follow-up**: *"What HTTP header is commonly used for client-driven idempotency?"*
* **Response**: *"The `Idempotency-Key` header, checked against a Redis store before executing business logic."*
* **If You Don't Know**: *"Currently it allows duplicate inserts; we should add unique constraints or deduplication keys."*

#### Q60: What happens if `json.loads` encounters a single malformed character?
* **What they are testing**: Parsing resilience.
* **Strong Answer**: *"Standard `json.loads` raises a `json.JSONDecodeError` immediately, rejecting the entire payload. In our code, `search_agent.py` catches this exception, prints the error, and initializes empty lists for accommodations and flights so the graph does not crash."*
* **Likely Follow-up**: *"Is there a more resilient alternative to `json.loads`?"*
* **Response**: *"Using `json_repair` or `dirtyjson` packages, which can parse partially formed JSON or recover from unescaped quotes."*
* **If You Don't Know**: *"It throws a JSONDecodeError, which our code catches in an except block."*

#### Q61: What are Deadlocks and could they occur in this architecture?
* **What they are testing**: Concurrency and database locking mechanics.
* **Strong Answer**: *"A deadlock occurs when two transactions each hold a lock the other needs. With a single SQLite database, deadlocks are rare, but lock contention occurs when multiple writers wait for the file lock. In a production PostgreSQL setup, deadlocks could occur if multiple threads updated route and price tables in opposing orders."*
* **Likely Follow-up**: *"How do you prevent database deadlocks?"*
* **Response**: *"Always acquire locks in a consistent, deterministic order and keep transactions as short as possible."*
* **If You Don't Know**: *"Deadlocks happen when processes block each other waiting for locks."*

#### Q62: What is the difference between at-least-once and at-most-once delivery?
* **What they are testing**: Messaging reliability.
* **Strong Answer**: *"'At-most-once' means messages are never redelivered (risk of data loss). 'At-least-once' means messages are redelivered until acknowledged (risk of duplicate processing). In a travel booking system, we want at-least-once delivery with idempotent consumer handlers to avoid double-charging or missing bookings."*
* **Likely Follow-up**: *"How do consumers achieve idempotency with at-least-once delivery?"*
* **Response**: *"By storing processed message IDs in a database or Redis and skipping duplicates."*
* **If You Don't Know**: *"At-least-once guarantees delivery but may duplicate; at-most-once prevents duplicates but may lose messages."*

#### Q63: How do you prevent thread starvation in Uvicorn/FastAPI?
* **What they are testing**: Server concurrency tuning.
* **Strong Answer**: *"By ensuring blocking I/O calls do not run on the main asyncio event loop, and by configuring the threadpool size in AnyIO or running multiple Uvicorn worker processes behind Gunicorn with `--workers 4`."*
* **Likely Follow-up**: *"How many workers should you run per server?"*
* **Response**: *"A standard heuristic for I/O bound workloads is `(2 * CPU_cores) + 1`."*
* **If You Don't Know**: *"By increasing worker processes and avoiding blocking the main event loop."*

#### Q64: What is exponential backoff with jitter?
* **What they are testing**: Distributed retry algorithms.
* **Strong Answer**: *"It is an algorithm for retrying failed network requests where the wait time doubles after each failure ($t = 2^n$), and 'jitter' adds a randomized time offset. This prevents the 'thundering herd' problem where thousands of clients retry simultaneously and overwhelm the recovered service."*
* **Likely Follow-up**: *"Where should this be applied in your project?"*
* **Response**: *"On calls to Groq and AviationStack when receiving HTTP 429 or 503 status codes."*
* **If You Don't Know**: *"It spaces out retries exponentially with random variation to avoid crashing recovering services."*

#### Q65: How do you handle database migration in SQLite vs PostgreSQL?
* **What they are testing**: Schema evolution and database operations.
* **Strong Answer**: *"In our current code, tables are created with `CREATE TABLE IF NOT EXISTS` at runtime. In production, this is dangerous because modifying columns requires migrations. We would use Alembic with SQLAlchemy to write versioned, reversible schema migration scripts."*
* **Likely Follow-up**: *"Why does SQLite make schema changes difficult?"*
* **Response**: *"Older SQLite versions have limited `ALTER TABLE` support (cannot easily drop or modify columns without copying the table)."*
* **If You Don't Know**: *"We use `CREATE TABLE IF NOT EXISTS` now, but production requires a migration tool like Alembic."*

#### Q66: What is the impact of memory leaks in long-running Python backend servers?
* **What they are testing**: Memory management and garbage collection.
* **Strong Answer**: *"Unreleased references (like growing global dictionaries or unclosed database connections) cause Python's heap to expand, eventually triggering the OS OOM (Out Of Memory) killer. In our code, states are scoped to request lifecycles and garbage collected when the request completes."*
* **Likely Follow-up**: *"How do you diagnose memory leaks in Python?"*
* **Response**: *"Using tools like `tracemalloc`, `objgraph`, or analyzing memory profiles in Grafana."*
* **If You Don't Know**: *"They consume server RAM over time until the server crashes."*

#### Q67: What happens if an API returns an HTTP 429 Too Many Requests?
* **What they are testing**: Rate-limiting compliance.
* **Strong Answer**: *"The HTTP client throws an HTTP error. In `flight_api_agent.py`, `resp.raise_for_status()` will raise an `HTTPError`, which the `try...except` block catches and logs, falling back to LLM flights. In production, we should parse the `Retry-After` header and delay before retrying."*
* **Likely Follow-up**: *"What status code should our API return if our own users exceed rate limits?"*
* **Response**: *"HTTP 429 Too Many Requests."*
* **If You Don't Know**: *"The client catches the exception and falls back to default state."*

#### Q68: How do you secure database credentials in code?
* **What they are testing**: Secrets management best practices.
* **Strong Answer**: *"Never hardcode credentials in source code. Use environment variables injected at runtime, store secrets in HashiCorp Vault or AWS Secrets Manager, and ensure `.env` is listed in `.gitignore`."*
* **Likely Follow-up**: *"What should you do if an API key is accidentally committed to Git?"*
* **Response**: *"Immediately revoke and rotate the key in the provider console, remove it from git history using `git-filter-repo` or BFG, and force-push."*
* **If You Don't Know**: *"Store them in environment variables and never commit them to version control."*

#### Q69: What is the difference between pessimistic and optimistic locking?
* **What they are testing**: Database concurrency controls.
* **Strong Answer**: *"Pessimistic locking locks the database record upfront (`SELECT ... FOR UPDATE`), preventing anyone else from reading or writing until done. Optimistic locking allows concurrent reads and writes, but verifies a version column before committing; if the version changed, the transaction aborts and retries."*
* **Likely Follow-up**: *"Which would you use for booking a hotel room?"*
* **Response**: *"Pessimistic locking during checkout to prevent double-booking the last available room."*
* **If You Don't Know**: *"Pessimistic locks upfront; optimistic checks for conflicts at commit time."*

#### Q70: What is graceful degradation in software engineering?
* **What they are testing**: Architectural resilience principles.
* **Strong Answer**: *"Graceful degradation means that when one component fails, the entire application does not crash, but instead continues operating with reduced functionality. For example, if our weather API fails, the user still receives hotel and flight recommendations with a notice that weather is unavailable."*
* **Likely Follow-up**: *"Give another example from your project."*
* **Response**: *"If AviationStack flight validation fails, the system falls back to LLM-generated flight estimates rather than returning a 500 error."*
* **If You Don't Know**: *"The system stays functional with reduced features when non-critical parts fail."*

#### Q71: How does connection pooling improve performance?
* **What they are testing**: Database connection reuse.
* **Strong Answer**: *"Establishing a database connection requires a TCP handshake, authentication, and session setup (often taking 20-50ms). A connection pool maintains a pool of open, authenticated connections that worker threads borrow and return, reducing connection latency to near zero."*
* **Likely Follow-up**: *"What tool provides connection pooling for PostgreSQL?"*
* **Response**: *"`PgBouncer` or built-in connection pooling in SQLAlchemy/asyncpg."*
* **If You Don't Know**: *"It reuses existing open database connections instead of creating a new one each time."*

#### Q72: What is the Cache Stampede (or Thundering Herd) problem?
* **What they are testing**: Caching failure modes.
* **Strong Answer**: *"When a popular cache key expires or is missing, hundreds of concurrent requests experience a cache miss simultaneously and all query the database or LLM at the same time, overwhelming the upstream service."*
* **Likely Follow-up**: *"How do you prevent a cache stampede?"*
* **Response**: *"By using distributed locking (e.g., Redis `SETNX`) so only one thread recomputes the cache, or using probabilistic early expiration (XFetch)."*
* **If You Don't Know**: *"When many concurrent requests miss the cache at once and overwhelm the database."*

#### Q73: What is the difference between process-level and thread-level concurrency?
* **What they are testing**: Operating system and concurrency basics.
* **Strong Answer**: *"Threads share the same memory space and are lightweight, but risk data races and are bounded by Python's GIL. Processes have isolated memory spaces, do not share the GIL, and provide true multi-core parallelism, but have higher memory overhead and require IPC (Inter-Process Communication)."*
* **Likely Follow-up**: *"How does Uvicorn utilize multi-process concurrency?"*
* **Response**: *"By spawning multiple worker processes behind a master socket using the `--workers` flag."*
* **If You Don't Know**: *"Threads share memory; processes have separate memory."*

#### Q74: Why is it bad practice to catch bare `except:` in Python?
* **What they are testing**: Python error handling best practices.
* **Strong Answer**: *"A bare `except:` catches `BaseException`, which includes system-exiting exceptions like `KeyboardInterrupt` (Ctrl+C) and `SystemExit`. It prevents clean server shutdown. Best practice is to catch specific exceptions or at least `except Exception:`."*
* **Likely Follow-up**: *"Did your project have any bare `except:` blocks?"*
* **Response**: *"In `weather_agent.py`, bare `except:` was used initially for rapid prototyping; I would refactor it to catch `requests.RequestException` and `KeyError` specifically."*
* **If You Don't Know**: *"Because it catches system signals like Ctrl+C and masks unexpected bugs."*

#### Q75: How does HTTP keep-alive affect connection overhead?
* **What they are testing**: Networking fundamentals.
* **Strong Answer**: *"HTTP Keep-Alive allows multiple HTTP requests and responses to be sent over a single persistent TCP connection, eliminating the repeated overhead of three-way TCP handshakes and TLS negotiations."*
* **Likely Follow-up**: *"Does `requests.get()` use keep-alive by default?"*
* **Response**: *"No, calling `requests.get()` directly opens and closes connections; using a `requests.Session()` maintains a persistent connection pool with keep-alive."*
* **If You Don't Know**: *"It reuses an existing TCP connection for multiple HTTP requests."*

---
