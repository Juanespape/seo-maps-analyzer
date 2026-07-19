# SEO Maps Analyzer — Geographic Boundaries Bot

Python tool that maps where a local business actually ranks on Google Maps across a metro
area, and turns that into a prioritized expansion plan.

## The problem

A local service business ranks well in its home city and assumes it dominates the region.
It usually doesn't. Visibility drops off sharply with distance, and the drop-off is uneven —
some cities 15 km away are easy wins while others 5 km away are locked up by entrenched
competitors. Without measuring it, expansion decisions are guesswork.

## What it does

Runs a systematic sweep of Google Maps searches across cities grouped into distance tiers,
records where the business appears (or doesn't), profiles the competition in each location,
and produces a coverage map plus a ranked list of expansion targets.

- Tests visibility across 25+ cities in four distance tiers
- Tracks ranking position per city/keyword pair (top 20 results)
- Profiles competitor density, average rating and review counts per location
- Persists every run to PostgreSQL so trends are comparable over time
- Outputs a dominance map and phase-based expansion recommendations with difficulty scoring

**Scale:** ~1,000+ search queries per full analysis cycle.

### Distance tiers

| Tier | Radius | Meaning |
|---|---|---|
| 1 | 0–5 km | Immediate dominance zone |
| 2 | 5–10 km | Near-term expansion targets |
| 3 | 10–15 km | Strategic opportunities |
| 4 | 15–25 km | ROI evaluation zone |

## Running it

```bash
git clone https://github.com/Juanespape/seo-maps-analyzer.git
cd seo-maps-analyzer
pip install -r requirements.txt

cp .env.example .env      # then fill in your values
python geographic_seo_analyzer.py
```

You need a **Google Maps Places API key** and a **PostgreSQL** database. All configuration
lives in `.env` — the business being analyzed, its coordinates, keywords and DB credentials
are variables, so the tool is not hardcoded to any one company.

## Technical decisions

**Distance-tiered sampling instead of a uniform radius.** A flat radius wastes API calls on
places that are either trivially won or hopeless. Grouping cities into tiers makes the
output directly actionable: tier 2 is where you spend money next, tier 4 is where you check
the math first.

**Haversine distance computed locally, not fetched.** Great-circle distance between two
coordinate pairs is cheap arithmetic. Calling an API for it would add latency and quota cost
per city pair with no benefit.

**PostgreSQL over flat files.** The point of the tool is comparing runs over time — did the
push into tier 2 actually move rankings? That is a query, not a diff of CSVs.

**Business identity matching is fuzzy by design** (`_es_tu_negocio`). Google Maps returns
business names with inconsistent suffixes, punctuation and casing, so an exact string match
silently reports "not ranking" when the business is right there. Matching tolerates those
variations.

**Randomized pacing between requests.** Places API enforces rate limits; jittered delays
keep a long sweep from tripping them and losing a whole run.

**Credentials only via environment variables.** `.env` is gitignored and `.env.example`
documents what is needed — no key ever reaches the repository.

## Stack

Python 3 · Google Maps Places API · PostgreSQL (`psycopg2`) · `requests` · `python-dotenv`

## License

MIT
