# SECTION 3: COMPLETE ARCHITECTURE

## 2. System Architecture

### Current Implementation Architecture

The diagram below represents the exact components, communication protocols, and execution boundaries currently present in the codebase:

```text
+-------------------------------------------------------------------------+
|                              CLIENT TIER                                |
|  React 19 (Vite) Single Page Application (frontend/src/App.jsx)         |
|  - State: formData, results, loading, minRatingFilter                   |
|  - Client-side in-memory array filtering (hotel.rating >= minFilter)    |
+-------------------------------------------------------------------------+
                                    |
                         HTTP POST /api/plan-trip
                         JSON Payload: TripRequest
                                    v
+-------------------------------------------------------------------------+
|                              SERVER TIER                                |
|  FastAPI Application (api.py) - Uvicorn ASGI Runner                     |
|  - CORS Middleware (allow_origins=["*"])                                |
|  - Pydantic Validation: TripRequest -> TravelState                      |
|  - Instantiates & executes LangGraph pipeline: graph.invoke()           |
+-------------------------------------------------------------------------+
                                    |
                      Compiled StateGraph Execution
                                    v
+-------------------------------------------------------------------------+
|                         LANGGRAPH PIPELINE (graph.py)                   |
|                                                                         |
|  [Entry]                                                                |
|     |                                                                   |
|     v                                                                   |
|  +--------------------+       HTTPS GET                                 |
|  | Node 1: weather    | ----------------------> Open-Meteo REST API     |
|  +--------------------+                         (Geocoding & Forecast)  |
|     |                                                                   |
|     v                                                                   |
|  +--------------------+       SQL SELECT                                |
|  | Node 2: cache      | ----------------------> SQLite (travel_cache.db)|
|  +--------------------+                         (accommodations/flights)|
|     |                                                                   |
|     |---> [Conditional Edge: route_cache()]                             |
|           |                                                             |
|           +-- (Cache Miss: accommodations or flights empty)             |
|           |       |                                                     |
|           |       v                                                     |
|           |   +--------------------+  HTTPS POST                        |
|           |   | Node 3: live_search| -------------> Groq Cloud API      |
|           |   +--------------------+                (Qwen-27B LLM)      |
|           |       |                                                     |
|           |       v                                                     |
|           |   +--------------------+  HTTPS GET                         |
|           |   | Node 4: flight_api | -------------> AviationStack API   |
|           |   +--------------------+                (Flight data)       |
|           |       |                                                     |
|           |       v                                                     |
|           |   +--------------------+  SQL INSERT                        |
|           |   | Node 5: store      | -------------> SQLite Database     |
|           |   +--------------------+                                    |
|           |       |                                                     |
|           +-------+                                                     |
|           |                                                             |
|           v (Cache Hit)                                                 |
|  +-------------------------+                                            |
|  | Node 6: recommend_hotels|  Sorts by (-rating, +price), builds Google |
|  +-------------------------+  Search links                              |
|     |                                                                   |
|     v                                                                   |
|  +-------------------------+                                            |
|  | Node 7: recommend_flights Sorts by price ascending, keeps top 8      |
|  +-------------------------+                                            |
|     |                                                                   |
|     v                                                                   |
|   [END]                                                                 |
+-------------------------------------------------------------------------+
                                    |
                       HTTP 200 JSON Response Payload
                                    v
+-------------------------------------------------------------------------+
|  Returned to Client:                                                    |
|  { weather_summary, recommended_hotels, flights }                       |
+-------------------------------------------------------------------------+
```

#### Architectural Realities (What Exists vs What Does Not)
* **CURRENT IMPLEMENTATION**:
  * A single synchronous process running FastAPI and LangGraph in-process.
  * Local single-file SQLite database (`travel_cache.db`) accessed via standard Python `sqlite3`.
  * Stateless REST API where the LangGraph graph is compiled and invoked per HTTP request.
  * Direct outbound HTTPS requests via `requests` library to external services (Open-Meteo, Groq, AviationStack).
* **NOT CURRENTLY IMPLEMENTED**:
  * No distributed cache (Redis/Memcached).
  * No asynchronous background task queues (Celery, RabbitMQ, Kafka).
  * No reverse proxy or load balancer (Nginx, AWS ALB, Traefik).
  * No user authentication, session tokens, or JWT authorization.
  * No database connection pooling (a new SQLite connection is opened and closed per node execution).

---

### Production-Scale Architecture

To scale this travel planning engine to enterprise volume (100,000+ daily active users and high-concurrency peak travel seasons), the following production architecture is recommended:

```text
                              [ Clients: Web & Mobile ]
                                         |
                                         v
                         +-------------------------------+
                         | Cloudflare CDN & WAF / DDoS   |
                         | - Static asset caching (React)|
                         | - TLS 1.3 termination         |
                         | - Rate limiting & bot defense |
                         +-------------------------------+
                                         |
                                         v
                         +-------------------------------+
                         |   Application Load Balancer   |
                         |   (AWS ALB / NGINX Ingress)   |
                         |   - Round-robin / Least Conn  |
                         |   - Active Health Checks      |
                         +-------------------------------+
                                         |
                  +----------------------+----------------------+
                  |                                             |
                  v                                             v
     +-------------------------+                   +-------------------------+
     |   FastAPI Service Pod 1 |                   |   FastAPI Service Pod N |
     |   (Stateless REST API)  |                   |   (Stateless REST API)  |
     +-------------------------+                   +-------------------------+
                  |                                             |
                  +----------------------+----------------------+
                                         |
                                         v
                 +-----------------------------------------------+
                 |              Redis Cache Cluster              |
                 |  - Distributed Cache-Aside (Route TTL: 6 hrs) |
                 |  - Rate-Limiting token buckets (by API key/IP)|
                 |  - Deduplication lock on concurrent searches  |
                 +-----------------------------------------------+
                                         |
                    (Cache Miss: Async Search Job Published)
                                         v
                 +-----------------------------------------------+
                 |          RabbitMQ / Kafka Message Bus         |
                 |   Topic: `travel.search.requests`             |
                 +-----------------------------------------------+
                                         |
                 +-----------------------+-----------------------+
                 |                                               |
                 v                                               v
     +-------------------------+                   +-------------------------+
     | LangGraph Worker Pod 1  |                   | LangGraph Worker Pod N  |
     | (Celery / FastStream)   |                   | (Celery / FastStream)   |
     | - Weather execution     |                   | - Weather execution     |
     | - Groq LLM resilience   |                   | - Groq LLM resilience   |
     | - AviationStack enrich  |                   | - AviationStack enrich  |
     +-------------------------+                   +-------------------------+
                  |                                             |
                  +----------------------+----------------------+
                                         |
                   WebSocket Push / Redis PubSub back to Client
                                         |
                                         v
                 +-----------------------------------------------+
                 |       PostgreSQL Primary-Replica Cluster      |
                 |   - Primary: Fast write persistence           |
                 |   - Read Replicas: Route queries & historical |
                 |   - Connection Pool: PgBouncer                |
                 +-----------------------------------------------+
                                         |
                                         v
                 +-----------------------------------------------+
                 |       Observability: Datadog / OpenTelemetry  |
                 |       (Tracing, Prometheus, Grafana, Sentry)  |
                 +-----------------------------------------------+
```

#### Why Each Proposed Component Exists:
1. **Cloudflare CDN / WAF**: Protects against Layer 7 DDoS attacks, terminates TLS closer to the user (reducing handshake latency), and serves static React assets from edge caches without touching application servers.
2. **Stateless FastAPI Application Tier**: Decoupled from background agent processing. Instead of holding long-lived HTTP connections while LLMs think, the API validates requests, checks the distributed cache, enqueues work, and returns immediately with a task ID or streams events via WebSockets.
3. **Redis Cluster**: Replaces the single-instance SQLite file with an in-memory distributed cache accessible across all container replicas. Stores cached route results with a 6-to-24-hour TTL, mitigating cache stampedes and preventing duplicate LLM billing.
4. **RabbitMQ / Kafka Queue**: Decouples search requests from worker processing. During traffic spikes, searches queue gracefully rather than overwhelming external rate limits on Groq or AviationStack.
5. **PostgreSQL with PgBouncer**: Replaces SQLite to support high-concurrency ACID transactions, connection pooling, and separate read/write workloads across primary and read-replica instances.
6. **OpenTelemetry & Prometheus**: Collects distributed trace context across HTTP handlers, LLM completion calls, database queries, and external API latency.

---
