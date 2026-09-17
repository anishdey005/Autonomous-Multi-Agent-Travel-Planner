### Category D: Scalability, Distributed Systems & System Design [Q76 – Q105]

#### Q76: Where would you introduce Redis in this system?
* **What they are testing**: Caching architecture and Redis integration.
* **Strong Answer**: *"I would place Redis as a distributed cache-aside layer in front of the database. When a search comes in, we check Redis with key `route:{origin}:{destination}`. If present, we return in <5ms. If absent, we acquire a distributed lock, execute the search, store the result with a 6-hour TTL, and return."*
* **Likely Follow-up**: *"What Redis data structure would you use?"*
* **Response**: *"A Redis String containing serialized JSON, or a Redis Hash if we wanted to read and update hotels and flights independently."*
* **If You Don't Know**: *"As an in-memory cache to store route search results with a time-to-live."*

#### Q77: Would you use Kafka or RabbitMQ to queue search tasks?
* **What they are testing**: Messaging system trade-offs.
* **Strong Answer**: *"RabbitMQ. Our search workload consists of discrete transactional jobs (fetch travel plan, update state, notify user). RabbitMQ provides granular task acknowledgments, dead-letter exchanges, and worker priority queues out of the box. Kafka is designed for high-throughput immutable event logs, which would be over-engineering for job queuing."*
* **Likely Follow-up**: *"When would you use Kafka instead?"*
* **Response**: *"If we were streaming user click events, tracking real-time price tick feeds from thousands of flights, or feeding real-time analytics to multiple independent consumers."*
* **If You Don't Know**: *"RabbitMQ for task queuing; Kafka for large-scale event streaming."*

#### Q78: How would you scale the system to handle 10,000 concurrent requests?
* **What they are testing**: High-scale system design.
* **Strong Answer**: *"1) Deploy stateless FastAPI instances horizontally behind an Application Load Balancer. 2) Move caching from SQLite to an Amazon ElastiCache Redis cluster. 3) Decouple search execution by returning a task ID and processing the LangGraph graph via Celery workers backed by RabbitMQ. 4) Push results back to the client via WebSockets."*
* **Likely Follow-up**: *"How do you prevent the external APIs from crashing under that load?"*
* **Response**: *"Through Redis rate-limiting (token bucket) and aggressive route caching so 70-80% of searches never touch the external APIs."*
* **If You Don't Know**: *"Horizontal scaling of stateless servers, Redis caching, and background worker queues."*

#### Q79: What is Database Sharding and when would you shard this database?
* **What they are testing**: Horizontal database partitioning.
* **Strong Answer**: *"Sharding partitions a database horizontally across multiple physical database servers. We would shard if the accommodations or flight bookings table grew to hundreds of millions of rows, exceeding the storage or write IOPS of a single large instance. We could shard by `destination_country` or hash of `route`."*
* **Likely Follow-up**: *"What is the main downside of sharding?"*
* **Response**: *"Cross-shard queries and distributed joins become complex, slow, and expensive."*
* **If You Don't Know**: *"Partitioning data across multiple database servers based on a shard key."*

#### Q80: How do Read Replicas work in relational databases?
* **What they are testing**: Database scaling patterns.
* **Strong Answer**: *"A primary database instance handles all write operations (`INSERT`, `UPDATE`, `DELETE`) and replicates its write-ahead log (WAL) asynchronously to multiple read-only replica instances. In our app, search queries read from replicas, while new route caches write to the primary."*
* **Likely Follow-up**: *"What is replication lag?"*
* **Response**: *"The brief delay before a write to the primary appears on a read replica, which can cause slightly stale reads."*
* **If You Don't Know**: *"The master handles writes, while read replicas handle search queries to distribute load."*

#### Q81: What is a CDN and how does it benefit this application?
* **What they are testing**: Content Delivery Networks and edge caching.
* **Strong Answer**: *"A CDN (like Cloudflare or AWS CloudFront) caches static assets (HTML, CSS, compiled JS, hotel images) at edge locations geographically close to users. It drastically reduces initial page load time and protects our origin server from static file traffic."*
* **Likely Follow-up**: *"Can dynamic API responses be cached on a CDN?"*
* **Response**: *"Yes, read-only search responses can be cached at the edge for short intervals using `Cache-Control: public, max-age=300` headers."*
* **If You Don't Know**: *"It caches static website files globally close to the user."*

#### Q82: How does the Token Bucket rate-limiting algorithm work?
* **What they are testing**: Rate limiting implementation.
* **Strong Answer**: *"A bucket has a maximum capacity of tokens and refills at a constant rate. Each user request requires one token. If tokens are available, the request is processed and a token is consumed. If the bucket is empty, requests are rejected with HTTP 429 until tokens refill."*
* **Likely Follow-up**: *"How do you implement this in Redis?"*
* **Response**: *"Using a Redis Lua script or Redis cell module to atomically check and decrement tokens based on timestamp."*
* **If You Don't Know**: *"It allows bursts of requests up to bucket capacity and refills at a steady rate."*

#### Q83: How do WebSockets differ from HTTP polling for travel search results?
* **What they are testing**: Real-time communication protocols.
* **Strong Answer**: *"HTTP polling requires the client to send repeated HTTP requests every 1-2 seconds asking 'is my trip ready?', wasting bandwidth and server resources. WebSockets establish a single full-duplex TCP connection where the server pushes the completed itinerary to the client the instant workers finish."*
* **Likely Follow-up**: *"What is Server-Sent Events (SSE) and is it better than WebSockets here?"*
* **Response**: *"SSE is unidirectional (server to client) over standard HTTP, making it simpler than WebSockets and ideal for streaming node completion events in a travel search pipeline."*
* **If You Don't Know**: *"WebSockets allow the server to push results instantly without repeated client requests."*

#### Q84: What is the difference between horizontal and vertical scaling?
* **What they are testing**: Fundamental scaling concepts.
* **Strong Answer**: *"Vertical scaling ('scaling up') means adding more CPU, RAM, or faster disks to a single server. Horizontal scaling ('scaling out') means adding more server instances behind a load balancer. Horizontal scaling is preferred because it eliminates single points of failure."*
* **Likely Follow-up**: *"What makes an application easy to scale horizontally?"*
* **Response**: *"Being stateless: storing no session state in server memory, so any server can handle any request."*
* **If You Don't Know**: *"Vertical is bigger servers; horizontal is more servers."*

#### Q85: What is Consistent Hashing and where is it used?
* **What they are testing**: Advanced distributed caching.
* **Strong Answer**: *"Consistent hashing maps keys and servers onto a virtual hash ring. When a cache server is added or removed, only $K/N$ keys need to be remapped (where $K$ is keys and $N$ is servers), avoiding a complete cache flush and system stampede."*
* **Likely Follow-up**: *"Where is consistent hashing used?"*
* **Response**: *"In distributed caching clusters like Memcached, Redis Cluster, and distributed databases like Cassandra."*
* **If You Don't Know**: *"A hashing technique that minimizes key remapping when servers are added or removed."*

#### Q86: How would you monitor this application in production?
* **What they are testing**: Production observability.
* **Strong Answer**: *"The Three Pillars of Observability: 1) Metrics: Prometheus scraping request rates, p95 latencies, error rates, and cache hit ratios, visualized in Grafana. 2) Logs: Structured JSON logs shipped via FluentBit to OpenSearch or Datadog. 3) Traces: OpenTelemetry tracing request spans across FastAPI, LangGraph nodes, and external APIs."*
* **Likely Follow-up**: *"What alert would you set as the highest priority (P0)?"*
* **Response**: *"An alert on HTTP 5xx error rate exceeding 1% over a 5-minute window or API latency exceeding 10 seconds."*
* **If You Don't Know**: *"Using metrics in Prometheus/Grafana, centralized logging, and distributed tracing."*

#### Q87: What is Blue-Green Deployment?
* **What they are testing**: Zero-downtime deployment strategies.
* **Strong Answer**: *"Maintaining two identical production environments: 'Blue' (running current live traffic) and 'Green' (where the new version is deployed and tested). Once verified, the load balancer router instantly switches traffic from Blue to Green with zero downtime."*
* **Likely Follow-up**: *"What if the new version has a critical bug?"*
* **Response**: *"Instant rollback by switching the load balancer back to the Blue environment."*
* **If You Don't Know**: *"Deploying to an idle environment and switching traffic instantly when ready."*

#### Q88: What is Canary Deployment?
* **What they are testing**: Incremental rollout strategies.
* **Strong Answer**: *"Deploying the new version to a small subset of servers (e.g., 5% of traffic) to monitor error rates and latency metrics in production. If metrics remain healthy, traffic is incrementally ramped up to 100%."*
* **Likely Follow-up**: *"How does this differ from Blue-Green?"*
* **Response**: *"Blue-Green switches all traffic at once; Canary rolls out gradually to minimize the blast radius of potential bugs."*
* **If You Don't Know**: *"Releasing the update to a small percentage of users first to verify stability."*

#### Q89: How would you handle user authentication and session management at scale?
* **What they are testing**: Auth architecture.
* **Strong Answer**: *"Using stateless JWT (JSON Web Tokens) signed via asymmetric cryptography (RS256). The client sends the token in the `Authorization: Bearer <token>` header. Any backend server can verify the token signature using the public key without querying a database or session store."*
* **Likely Follow-up**: *"How do you invalidate a JWT before it expires if a user logs out?"*
* **Response**: *"Store revoked token IDs (JTI) in a Redis blacklist with a TTL equal to the remaining token lifetime."*
* **If You Don't Know**: *"Using JWT tokens so servers can verify authentication without database lookups."*

#### Q90: What is the CAP theorem and what trade-off does this system make?
* **What they are testing**: Distributed systems theory.
* **Strong Answer**: *"CAP states that in a distributed data store experiencing a network partition (P), you must choose between Consistency (C) or Availability (A). For travel search caching, we choose Availability and Partition Tolerance (AP)—it is better to return slightly stale flight prices from cache than to fail the user's request."*
* **Likely Follow-up**: *"When would you choose Consistency (CP) in travel?"*
* **Response**: *"During actual seat reservation and credit card payment processing."*
* **If You Don't Know**: *"In a partition, choosing between consistent data or always-available responses."*

#### Q91: How does Kubernetes Horizontal Pod Autoscaler (HPA) work?
* **What they are testing**: Container orchestration and auto-scaling.
* **Strong Answer**: *"HPA monitors metrics (like CPU utilization, memory usage, or custom metrics like queue depth) and automatically scales the number of replica pods up or down within defined min and max boundaries."*
* **Likely Follow-up**: *"Why might scaling on CPU alone be problematic for our backend?"*
* **Response**: *"Because our workload is I/O-bound (waiting on external APIs); workers can be saturated without high CPU utilization. Scaling on request latency or queue depth is more effective."*
* **If You Don't Know**: *"It automatically adds or removes container pods based on resource usage."*

#### Q92: What is the difference between L4 and L7 load balancing?
* **What they are testing**: Networking layers.
* **Strong Answer**: *"L4 (Transport Layer) balances traffic based on IP addresses and TCP/UDP ports without inspecting packet contents. L7 (Application Layer) inspects HTTP/HTTPS headers, cookies, and URL paths, allowing intelligent routing (e.g., routing `/api` to FastAPI and `/` to React)."*
* **Likely Follow-up**: *"Which would you use for this project?"*
* **Response**: *"L7 load balancing (like AWS ALB or NGINX Ingress) to route API requests separately from static assets."*
* **If You Don't Know**: *"L4 routes on IP and port; L7 routes on HTTP headers and paths."*

#### Q93: How would you design an alert for flight price drops?
* **What they are testing**: System design for asynchronous cron jobs.
* **Strong Answer**: *"1) Store user alert subscriptions (`user_id`, `route`, `target_price`) in PostgreSQL. 2) A Celery Beat or cron job periodically publishes route checks to a RabbitMQ queue. 3) Worker nodes check the cache or call AviationStack. 4) If current price is below target price, publish an event to send an email via SendGrid or push notification via Firebase."*
* **Likely Follow-up**: *"How do you prevent sending duplicate alerts?"*
* **Response**: *"Track `last_notified_at` timestamps in the database and enforce a cooldown period (e.g., max 1 alert per 24 hours)."*
* **If You Don't Know**: *"Use a background cron job to check prices periodically and send notifications on drops."*

#### Q94: What is Eventual Consistency?
* **What they are testing**: Data consistency models.
* **Strong Answer**: *"A consistency model in distributed systems where, given no new updates, all replicas will eventually return the same data. During the update propagation window, different replicas may return slightly different values."*
* **Likely Follow-up**: *"Where does eventual consistency occur in travel apps?"*
* **Response**: *"When a flight price updates, it may take several minutes to propagate across all edge caches and read replicas."*
* **If You Don't Know**: *"Data becomes consistent across all servers after a short synchronization period."*

#### Q95: How do you handle database failover without downtime?
* **What they are testing**: High availability database operations.
* **Strong Answer**: *"Using an automated multi-AZ (Availability Zone) setup like AWS Aurora or Patroni for PostgreSQL. If the primary crashes, a health-check monitor detects it, promotes a standby read replica to the primary, and updates the DNS or virtual IP with zero manual intervention."*
* **Likely Follow-up**: *"What happens to in-flight transactions during failover?"*
* **Response**: *"In-flight transactions abort and must be retried by the application layer."*
* **If You Don't Know**: *"By having an active standby replica that gets promoted automatically if the primary fails."*

#### Q96: What is a Reverse Proxy and how does it differ from a Forward Proxy?
* **What they are testing**: Proxy architecture.
* **Strong Answer**: *"A forward proxy acts on behalf of clients (e.g., a corporate proxy hiding internal users). A reverse proxy acts on behalf of servers (e.g., NGINX sitting in front of FastAPI to handle SSL termination, caching, compression, and request routing)."*
* **Likely Follow-up**: *"Why put NGINX in front of Uvicorn?"*
* **Response**: *"NGINX handles slow clients, static files, and SSL handshakes much more efficiently than Python application servers."*
* **If You Don't Know**: *"A forward proxy protects clients; a reverse proxy protects and manages servers."*

#### Q97: What is gRPC and when would you use it instead of REST?
* **What they are testing**: Inter-service communication protocols.
* **Strong Answer**: *"gRPC is a high-performance RPC framework using HTTP/2 and Protocol Buffers (Protobuf) for binary serialization. It is 5-10x faster than JSON over REST. We would use it for internal microservice-to-microservice communication, while keeping REST/JSON for public client communication."*
* **Likely Follow-up**: *"Why keep REST for frontend clients?"*
* **Response**: *"Browsers have native support for HTTP/JSON, and REST is easier to inspect and debug in browser DevTools."*
* **If You Don't Know**: *"gRPC uses binary Protobuf for fast internal service communication; REST is for public web APIs."*

#### Q98: How do you secure data in transit vs data at rest?
* **What they are testing**: Security engineering.
* **Strong Answer**: *"Data in transit is secured using TLS 1.3 (HTTPS), encrypting packets between client, load balancer, and backend services. Data at rest is encrypted using AES-256 at the storage volume level (e.g., AWS EBS encryption) and database level (TDE - Transparent Data Encryption)."*
* **Likely Follow-up**: *"How do you protect database backups?"*
* **Response**: *"Encrypt backup files with separate KMS (Key Management Service) keys and restrict access via strict IAM roles."*
* **If You Don't Know**: *"In transit uses HTTPS/TLS; at rest uses AES encryption on disk."*

#### Q99: What is the Single Point of Failure (SPOF) in your current architecture?
* **What they are testing**: Critical self-assessment of system design.
* **Strong Answer**: *"There are several: 1) The single SQLite file (`travel_cache.db`) on local disk. 2) The single FastAPI process running on a single port. 3) The single Groq API key without fallback providers. If any of these fails, the entire application fails."*
* **Likely Follow-up**: *"What is the first SPOF you would eliminate?"*
* **Response**: *"Migrate caching from the local SQLite file to a managed PostgreSQL/Redis cluster, allowing multiple FastAPI instances to run statelessly."*
* **If You Don't Know**: *"The single SQLite file and single server instance are single points of failure."*

#### Q100: If you were designing this as an enterprise SaaS for 10 million travelers, what would be your top priority?
* **What they are testing**: Executive architectural vision.
* **Strong Answer**: *"Decoupling synchronous request handling into an event-driven architecture. Users should never wait synchronously on external LLM and API responses. I would return immediate task receipts, stream itinerary updates via Server-Sent Events, warm cache tiers proactively for popular travel routes, and maintain multi-region database redundancy."*
* **Likely Follow-up**: *"How would you control LLM inference costs at that scale?"*
* **Response**: *"Aggressive 24-hour route caching, smaller fine-tuned models for extraction, and semantic cache deduplication to serve repeat queries without burning LLM tokens."*
* **If You Don't Know**: *"Decoupling requests into asynchronous background jobs, caching popular routes, and optimizing external API costs."*

---
