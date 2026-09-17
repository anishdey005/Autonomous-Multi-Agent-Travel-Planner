# SECTION 7: DATABASE DEEP DIVE

## 6. Database Deep Dive

### Database Schema in Current Implementation

The project uses a single SQLite database file: `travel_cache.db`. Tables are declared and initialized in [`database/sqlite_client.py:L17-45`](file:///d:/Programming/sde_projects/travelagent/database/sqlite_client.py#L17-L45).

```sql
-- Accommodations Table
CREATE TABLE IF NOT EXISTS accommodations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT,
    provider_item_id TEXT,
    name TEXT,
    city TEXT,
    country TEXT,
    bedrooms INTEGER,
    price_per_night REAL,
    rating REAL,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Flights Table
CREATE TABLE IF NOT EXISTS flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT,
    airline TEXT,
    origin TEXT,
    destination TEXT,
    depart_time TEXT,
    arrive_time TEXT,
    price REAL,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### Key Database Queries & Performance Analysis

#### Query 1: Destination Hotel Cache Lookup
* **Code Location**: [`database/cache.py:L13-24`](file:///d:/Programming/sde_projects/travelagent/database/cache.py#L13-L24)
* **SQL**:
  ```sql
  SELECT name, city, country, price_per_night, rating, url, bedrooms
  FROM accommodations
  WHERE LOWER(city) = LOWER(?)
  LIMIT 10;
  ```
* **Parameters**: `(state.destination,)`
* **Purpose**: Checks if hotels for this destination have already been cached from previous queries.
* **Cost & Optimization**:
  * **Current Cost**: **O(N) Full Table Scan**. Because `LOWER(city)` is wrapped in an expression without an index, SQLite must evaluate the `LOWER()` function across every row in the table.
  * **Optimization**: Add a case-insensitive collation index:
    ```sql
    CREATE INDEX idx_accommodations_city_nocase ON accommodations(city COLLATE NOCASE);
    ```
    Then query using: `WHERE city = ? COLLATE NOCASE LIMIT 10;` dropping lookup time from O(N) to **O(log N)**.

#### Query 2: Route Flight Cache Lookup
* **Code Location**: [`database/cache.py:L29-39`](file:///d:/Programming/sde_projects/travelagent/database/cache.py#L29-L39)
* **SQL**:
  ```sql
  SELECT airline, origin, destination, price, url
  FROM flights
  WHERE origin = ? AND destination = ?
  LIMIT 10;
  ```
* **Parameters**: `(state.origin, state.destination)`
* **Purpose**: Checks if flights for this exact origin-destination pair exist in the cache.
* **Cost & Optimization**:
  * **Current Cost**: **O(N) Full Table Scan**. No composite index exists on `(origin, destination)`.
  * **Optimization**: Add a composite B-Tree index:
    ```sql
    CREATE INDEX idx_flights_route ON flights(origin, destination);
    ```
    This reduces row retrieval complexity to **O(log N)**.

#### Query 3: Storing New Accommodations & Flights (Cache Miss)
* **Code Location**: [`database/store_results.py:L13-48`](file:///d:/Programming/sde_projects/travelagent/database/store_results.py#L13-L48)
* **SQL**:
  ```sql
  INSERT INTO accommodations (name, city, country, price_per_night, rating, url, bedrooms)
  VALUES (?, ?, ?, ?, ?, ?, ?);

  INSERT INTO flights (airline, origin, destination, price, url)
  VALUES (?, ?, ?, ?, ?);
  ```
* **Purpose**: Persists freshly generated LLM and API results.
* **Concurrency Consideration**: SQLite uses file-level locking. Calling `store_results` acquires an exclusive write lock. While fine for a single user, 100 concurrent requests would experience lock contention (`sqlite3.OperationalError: database is locked`). In production, this requires connection pooling and a database engine supporting row-level locking (PostgreSQL).

---

### Database Interview Questions & Prepared Answers

#### 1. Why SQL over NoSQL (like MongoDB) for this project?
> *"Even though travel search results are returned as JSON from the LLM, the data itself is highly relational and structured: accommodations belong to cities, flights connect specific origin and destination pairs, and users filter by discrete numeric columns like rating and price. Relational SQL allows parameterized filtering, composite indexing on routes, and strict column typing. In production, SQL ensures ACID compliance when booking transactions occur."*

#### 2. When would NoSQL make sense for this project?
> *"NoSQL would make sense if we began ingesting unpredictable, schema-less hotel amenities (e.g., swimming pools, pet friendly, parking, free breakfast) from dozens of disparate aggregator APIs where normalizing hundreds of sparse columns into a relational schema becomes unwieldy. A document store like MongoDB or PostgreSQL's `JSONB` data type would allow flexible, nested attribute indexing."*

#### 3. What happens if two users search and store the same route simultaneously?
> *"In the current SQLite implementation, the second write will wait briefly for the file lock, and both searches will insert duplicate rows for that city or route because there is no unique constraint. In production, we would add a unique composite constraint or hash on `(name, city)` and `(airline, origin, destination, depart_time)` and execute `INSERT ... ON CONFLICT DO NOTHING` (upsert), or use a distributed lock in Redis to ensure only one worker executes the live search for that route."*

#### 4. How would you handle cache invalidation and stale prices?
> *"Flight and hotel prices are highly dynamic. In our current implementation, records stay in SQLite indefinitely with a `created_at` timestamp. In production, we would implement a Cache-Aside pattern with TTL: records older than 6 hours are considered stale and trigger a background refresh, or we query `WHERE created_at > datetime('now', '-6 hours')` during cache checks."*

---
