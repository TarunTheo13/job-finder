# Job Finder

Uses firecrawl and OpenAI to scrape for jobs relevant to the CV.

## Setup

### Using Docker (Recommended)

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
- `FIRECRAWL_API_KEY`: Your Firecrawl API key
- `OPENAI_API_KEY`: Your OpenAI API key

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The API will be available at http://localhost:8000

### Manual Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the server:
```bash
python job_agent.py
```

## API Usage Example

```bash
curl -X 'POST' \
  'http://localhost:8000/analyze-jobs' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "resume": "Eric Ciarla\nCo-Founder @ Firecrawl\nSan Francisco, California, United States\nSummary\nBuilding...\nExperience\nFirecrawl\nCo-Founder\nApril 2024 - Present (6 months)\nSan Francisco, California, United States\nFirecrawl by Mendable. Building data extraction infrastructure for AI. Used by Amazon, Zapier, and Nvidia (YC S22)",
  "jobs_page_url": "https://www.google.com/about/careers/applications/jobs/results",
  "num_jobs": 3
}'
```

Example Response:
```json
{
  "recommended_jobs": [
    {
      "job_title": "Software Engineer, Data Infrastructure",
      "compensation": "$150,000 - $220,000/year",
      "apply_link": "https://careers.google.com/jobs/123"
    },
    {
      "job_title": "Senior Data Engineer",
      "compensation": "$160,000 - $230,000/year",
      "apply_link": "https://careers.google.com/jobs/456"
    },
    {
      "job_title": "Technical Lead, Data Systems",
      "compensation": "$180,000 - $250,000/year",
      "apply_link": "https://careers.google.com/jobs/789"
    }
  ]
}
```