from .sqlite_client import get_conn

def store_results(state):
    """
    Store freshly fetched accommodations and flights into SQLite.
    Called only on cache miss.
    """
    conn = get_conn()
    cur = conn.cursor()

    # Accommodations
    for h in state.accommodations:
        cur.execute(
            """
            INSERT INTO accommodations
                (name, city, country, price_per_night, rating, url, bedrooms)
            VALUES
                (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                h.get("name"),
                h.get("city"),
                h.get("country"),
                h.get("price") or h.get("price_per_night"),
                h.get("rating"),
                h.get("url"),
                h.get("bedrooms"),
            )
        )

    # Flights
    for f in state.flights:
        cur.execute(
            """
            INSERT INTO flights
                (airline, origin, destination, price, url)
            VALUES
                (?, ?, ?, ?, ?)
            """,
            (
                f.get("airline"),
                f.get("origin"),
                f.get("destination"),
                f.get("price"),
                f.get("url"),
            )
        )

    conn.commit()
    conn.close()