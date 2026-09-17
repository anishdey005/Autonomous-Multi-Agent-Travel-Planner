import { useState } from 'react'

function App() {
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    start_date: '',
    end_date: '',
    bedrooms: 1,
    max_price_per_night: 15000,
    min_rating: 1.0 // Sent internally to backend to fetch all, user filters later
  })

  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [minRatingFilter, setMinRatingFilter] = useState(0) // Default to all

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResults(null)
    setMinRatingFilter(0) // Reset filter on new search

    try {
      const response = await fetch('http://localhost:8000/api/plan-trip', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })

      if (!response.ok) {
        throw new Error('Failed to fetch travel plan. Please check your backend.')
      }

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const filteredHotels = results?.recommended_hotels?.filter(hotel => hotel.rating >= minRatingFilter) || [];

  return (
    <div className="container">
      <header className="header">
        <h1>Agentic AI Travel Planner</h1>
        <p>Powered by LangGraph, Groq Llama 3, and React</p>
      </header>

      <datalist id="cities">
        <option value="Bangalore" />
        <option value="BLR" />
        <option value="Mumbai" />
        <option value="BOM" />
        <option value="Delhi" />
        <option value="DEL" />
        <option value="Chennai" />
        <option value="MAA" />
        <option value="Hyderabad" />
        <option value="HYD" />
        <option value="Kolkata" />
        <option value="CCU" />
        <option value="Pune" />
        <option value="PNQ" />
        <option value="Goa" />
        <option value="GOI" />
      </datalist>

      <div className="glass-card">
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label>Origin</label>
              <input type="text" name="origin" list="cities" value={formData.origin} onChange={handleInputChange} placeholder="e.g., Bangalore or BLR" required />
            </div>
            <div className="form-group">
              <label>Destination</label>
              <input type="text" name="destination" list="cities" value={formData.destination} onChange={handleInputChange} placeholder="e.g., Mumbai or BOM" required />
            </div>
            <div className="form-group">
              <label>Start Date</label>
              <input type="date" name="start_date" value={formData.start_date} onChange={handleInputChange} required />
            </div>
            <div className="form-group">
              <label>End Date</label>
              <input type="date" name="end_date" value={formData.end_date} onChange={handleInputChange} required />
            </div>
            <div className="form-group">
              <label>Bedrooms</label>
              <input type="number" name="bedrooms" value={formData.bedrooms} onChange={handleInputChange} min="1" required />
            </div>
            <div className="form-group">
              <label>Max Price/Night (₹)</label>
              <input type="number" name="max_price_per_night" value={formData.max_price_per_night} onChange={handleInputChange} min="100" required />
            </div>
          </div>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? <><span className="spinner"></span> AI is Planning...</> : 'Generate Trip Plan ✈️'}
          </button>
        </form>
      </div>

      {error && (
        <div className="glass-card" style={{ marginTop: '2rem', borderLeft: '4px solid #ef4444' }}>
          <h3 style={{ color: '#ef4444' }}>Oops!</h3>
          <p>{error}</p>
        </div>
      )}

      {results && (
        <div className="results-section">
          {results.weather_summary && (
            <div className="weather-box">
              <h3>⛅ Weather Forecast</h3>
              <p>{results.weather_summary}</p>
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2 className="section-title" style={{ margin: 0 }}>🏨 Top Hotel Recommendations</h2>
            <div className="form-group" style={{ flexDirection: 'row', alignItems: 'center', gap: '0.8rem' }}>
              <label style={{ fontSize: '1rem', color: '#fff' }}>Filter by Rating:</label>
              <select 
                value={minRatingFilter} 
                onChange={(e) => setMinRatingFilter(Number(e.target.value))}
                style={{ padding: '0.4rem', borderRadius: '8px', background: 'rgba(0,0,0,0.4)', color: 'white', border: '1px solid var(--glass-border)' }}
              >
                <option value={0}>All Ratings</option>
                <option value={3}>3+ Stars</option>
                <option value={4}>4+ Stars</option>
                <option value={4.5}>4.5+ Stars</option>
              </select>
            </div>
          </div>
          
          {filteredHotels.length > 0 ? (
            <div className="items-grid">
              {filteredHotels.map((hotel, index) => (
                <div key={index} className="glass-card item-card">
                  <h3 className="item-title">{hotel.name}</h3>
                  <div className="item-meta">
                    <span>{hotel.city}, {hotel.country}</span>
                    <span className="badge">⭐ {hotel.rating}</span>
                  </div>
                  <div className="item-meta">
                    <span>{hotel.bedrooms} Bedroom(s)</span>
                    <span className="price">₹{hotel.price || hotel.price_per_night}/nt</span>
                  </div>
                  {hotel.url && <a href={hotel.url} target="_blank" rel="noreferrer" className="link-btn">View Details</a>}
                </div>
              ))}
            </div>
          ) : (
            <p>No hotel recommendations found matching your current filter.</p>
          )}

          <h2 className="section-title">✈️ Top Flight Options</h2>
          {results.flights?.length > 0 ? (
            <div className="items-grid">
              {results.flights.map((flight, index) => (
                <div key={index} className="glass-card item-card">
                  <h3 className="item-title">{flight.airline}</h3>
                  <div className="item-meta">
                    <span>{flight.origin} → {flight.destination}</span>
                  </div>
                  <div className="item-meta">
                    <span className="price">₹{flight.price}</span>
                  </div>
                  {flight.url && <a href={flight.url} target="_blank" rel="noreferrer" className="link-btn">Book Flight</a>}
                </div>
              ))}
            </div>
          ) : (
            <p>No flight options found for this route.</p>
          )}
        </div>
      )}
    </div>
  )
}

export default App
