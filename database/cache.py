from .sqlite_client import get_conn

def check_cache(state):
    """
    Check SQLite for cached hotels & flights for this route.
    If BOTH exist, it's a cache hit. Otherwise, return None (cache miss).
    """
    conn = get_conn()
    cur = conn.cursor()

    # Hotels for destination
    cur.execute("""
        SELECT
            name,
            city,
            country,
            price_per_night,
            rating,
            url,
            bedrooms
        FROM accommodations
        WHERE LOWER(city) = LOWER(?)
        LIMIT 10
    """, (state.destination,))
    
    hotels = [dict(row) for row in cur.fetchall()]

    # Flights for origin + destination
    cur.execute("""
        SELECT
            airline,
            origin,
            destination,
            price,
            url
        FROM flights
        WHERE origin = ? AND destination = ?
        LIMIT 10
    """, (state.origin, state.destination))
    
    flights = [dict(row) for row in cur.fetchall()]
    
    conn.close()

    if len(hotels) > 0 and len(flights) > 0:
        state.accommodations = hotels
        state.flights = flights
        return state

    # Cache miss
    return None