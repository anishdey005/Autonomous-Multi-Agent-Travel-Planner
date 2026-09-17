import json
import os
from openai import OpenAI


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[WARNING] GROQ_API_KEY is not set in environment!")
    return OpenAI(
        api_key=api_key or "missing_key",
        base_url="https://api.groq.com/openai/v1"
    )


def live_search(state):
    """
    Use Groq Chat Completions to generate accommodations + flights
    consistent with the user's inputs.
    """
    client = get_groq_client()

    system_prompt = """
You are a travel planning AI. You help users find hotels and flights.

You MUST respond with STRICT JSON only. No markdown, no explanations, no comments.
The JSON MUST have this exact structure (field names should ideally match):

{
  "accommodations": [
    {
      "name": "string",
      "city": "string",
      "country": "string",
      "price": 5000.0,
      "rating": 4.5,
      "bedrooms": 1,
      "url": "https://..."
    }
  ],
  "flights": [
    {
      "airline": "string",
      "origin": "string",
      "destination": "string",
      "price": 4500.0,
      "url": "https://..."
    }
  ]
}

Rules:
- All prices MUST be in Indian Rupees (INR / ₹) based on realistic estimates.
- All numbers must be valid JSON numbers (no commas in thousands, e.g. 15500.0 not 15,500.0).
- Return 8-12 accommodations.
- Return 5-8 flights.
- Try to respect user constraints (max price, min rating, bedrooms, route).
- Use realistic-sounding hotel names and airlines, but you may approximate.
    """.strip()

    user_prompt = f"""
User trip details:
- Origin: {state.origin}
- Destination: {state.destination}
- Start date: {state.start_date}
- End date: {state.end_date}
- Bedrooms needed: {state.bedrooms}
- Max hotel price per night: {state.max_price_per_night}
- Minimum hotel rating: {state.min_rating}
- Max flight price (if provided): {state.max_flight_price}

Generate hotels and flights that match these constraints as much as possible.

Return ONLY the JSON object as specified in the system message.
Do NOT include any additional keys, text, or markdown.
    """.strip()

    try:
        model_name = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )

        content = resp.choices[0].message.content.strip()

        print("\n--- RAW LLM OUTPUT ---")
        try:
            print(content)
        except Exception:
            pass
        print("--- END RAW LLM OUTPUT ---\n")

        # Strip ```json fences if present
        if content.startswith("```"):
            parts = content.split("```")
            if len(parts) >= 3:
                content = parts[1]
            content = content.replace("json", "", 1).strip()

        cleaned = (
            content.replace(",}", "}")
                   .replace(",]", "]")
        )

        data = json.loads(cleaned)

        # If nested under "result"/"data"/"response"
        if isinstance(data, dict) and "accommodations" not in data and "flights" not in data:
            for key in ["result", "data", "response"]:
                if isinstance(data.get(key), dict):
                    data = data[key]
                    break

        accommodations = (
            data.get("accommodations")
            or data.get("hotels")
            or data.get("places")
            or []
        )

        flights = (
            data.get("flights")
            or data.get("flight_options")
            or data.get("routes")
            or []
        )

        if not isinstance(accommodations, list):
            accommodations = []
        if not isinstance(flights, list):
            flights = []

        state.accommodations = accommodations
        state.flights = flights
        return state

    except Exception as e:
        print("[ERROR] live_search error, leaving results empty:", str(e).encode('ascii', 'ignore').decode('ascii'))
        state.accommodations = []
        state.flights = []
        return state