# Job Finder

Uses firecrawl and OpenAI to scrape for jobs relevant to the CV.

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