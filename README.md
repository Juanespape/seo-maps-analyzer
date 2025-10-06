# SEO Maps Analyzer - Geographic Boundaries Bot

Python automation tool that analyzes Google Maps SEO performance across geographic boundaries. Built to identify territorial dominance radius and strategic expansion opportunities for local service businesses.

## Overview

This bot performs automated geographic SEO analysis by:
- Testing business visibility across 25+ cities in different distance tiers
- Tracking ranking positions for core service keywords
- Analyzing competitor density and strength per location
- Generating actionable expansion recommendations
- Storing historical data for trend analysis

## Tech Stack

- **Python 3.x** - Core automation
- **Google Maps Places API** - Location data and search results
- **PostgreSQL** - Historical data storage and analysis
- **python-dotenv** - Secure credential management
- **requests** - API communication

## Key Features

### Multi-Tier Geographic Analysis
- **Tier 1 (0-5km)**: Immediate dominance zone
- **Tier 2 (5-10km)**: Near-term expansion targets
- **Tier 3 (10-15km)**: Strategic opportunities
- **Tier 4 (15-25km)**: ROI evaluation zone

### Real-Time Metrics
- Ranking position tracking (Top 20 results)
- Competitor count per location
- Average competitor ratings and review counts
- Distance calculations using Haversine formula
- Coverage percentage by tier

### Automated Reporting
- Visual dominance maps
- Strategic expansion recommendations
- Opportunity scoring (difficulty: Easy/Medium/Hard)
- Phase-based action plans

## Use Case

Built to optimize local SEO strategy for service-based businesses operating across multiple cities. Processes **1,000+ search queries per analysis cycle** to map competitive landscape and identify low-hanging fruit for geographic expansion.

## Configuration

Create a `.env` file with:

```bash
# Google Maps API
GOOGLE_MAPS_API_KEY=your_api_key_here

# Business Configuration
TARGET_DOMAIN=yourbusiness.com
BUSINESS_NAME=Your Business Name
BUSINESS_KEYWORDS=your,business,keywords

# Base Location
BASE_CITY=Los Angeles, CA
BASE_LAT=34.0522
BASE_LNG=-118.2437

# Database (PostgreSQL)
DB_HOST=localhost
DB_NAME=seo_analysis
DB_USER=postgres
DB_PASSWORD=your_password_here
```

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/seo-maps-analyzer.git
cd seo-maps-analyzer

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run analysis
python bot_fronteras_geograficas.py
```

## Requirements

```
requests>=2.31.0
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
```

## Sample Output

```
🗺️ GEOGRAPHIC BOUNDARIES ANALYSIS - GOOGLE MAPS
📍 Base: Los Angeles, CA
🎯 Business: Your Business Name

📏 DOMINANCE RADIUS:
   Effective dominance radius: ~12km
   Average Maps position: #2.3

🎯 TOP EXPANSION OPPORTUNITIES:
   1. Culver City (8.5km)
      Competitors: 18
      Avg rating: 4.2⭐
      Difficulty: MEDIUM
```

## Database Schema

Analysis results are stored in PostgreSQL for historical tracking:

```sql
CREATE TABLE maps_analisis_geografico (
    id SERIAL PRIMARY KEY,
    fecha_analisis DATE,
    ciudad VARCHAR(100),
    keyword VARCHAR(255),
    aparece BOOLEAN,
    posicion INTEGER,
    distancia_km DECIMAL(6,2),
    total_competidores INTEGER,
    rating_promedio_competidores DECIMAL(3,2)
);
```

## Performance

- **Analysis speed**: ~3 seconds per city/keyword combination
- **Rate limiting**: Built-in delays to respect API quotas
- **Data accuracy**: Real-time Google Maps results
- **Scalability**: Easily configurable for 50+ cities

## Future Enhancements

- [ ] Automated email reports
- [ ] Visualization dashboard (Plotly/Dash)
- [ ] Multi-language support
- [ ] Competitor tracking over time
- [ ] Integration with Google Search Console

## License

This project is for portfolio demonstration purposes.

---

*Built as part of my automation toolkit for local business SEO optimization*
