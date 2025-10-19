from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI

# Pydantic models
class JobRequest(BaseModel):
    resume: str
    jobs_page_url: Optional[str] = Field(default="https://www.google.com/about/careers/applications/jobs/results")
    num_jobs: Optional[int] = Field(default=3, gt=0, le=10)

class RecommendedJob(BaseModel):
    job_title: str
    compensation: str
    apply_link: str

class JobResponse(BaseModel):
    recommended_jobs: List[RecommendedJob]

# Initialize FastAPI app
app = FastAPI(
    title="Job Finder API",
    description="API for finding and analyzing job opportunities based on resume",
    version="1.0.0"
)

# Load environment variables
load_dotenv()

# Initialize clients
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def scrape_and_analyze_jobs(resume: str, jobs_page_url: str, num_jobs: int) -> List[RecommendedJob]:
    """
    Scrape jobs from the provided URL and analyze them against the resume.
    """
    print(f"Starting job analysis for URL: {jobs_page_url}")
    print(f"Requesting {num_jobs} jobs")
    try:
        # Scrape the jobs page
        response = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {firecrawl_api_key}"
            },
            json={
                "url": jobs_page_url,
                "formats": ["markdown"]
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to scrape jobs page")
            
        result = response.json()
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=f"Failed to scrape jobs page: {result.get('message', 'Unknown error')}")
        
        html_content = result['data']['markdown']
        print("Successfully scraped jobs page, extracting job links...")
        
        # Extract apply links using OpenAI
        prompt = f"""
        Extract up to {num_jobs} job application links from the given markdown content.
        Return the result as a JSON object with a single key 'apply_links' containing an array of strings (the links).
        The output should be a valid JSON object, with no additional text.

        Example of the expected format:
        {{"apply_links": ["https://example.com/job1", "https://example.com/job2", ...]}}

        Markdown content:
        {html_content[:100000]}
        """
        
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        apply_links = json.loads(completion.choices[0].message.content.strip())['apply_links']
        print(f"Found {len(apply_links)} job links, analyzing each job...")
        
        # Extract job details
        extracted_data = []
        for link in apply_links:
            response = requests.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {firecrawl_api_key}"
                },
                json={
                    "url": link,
                    "formats": ["extract"],
                    "actions": [{
                        "type": "click",
                        "selector": "#job-overview"
                    }],
                    "extract": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "job_title": {"type": "string"},
                                "sub_division_of_organization": {"type": "string"},
                                "key_skills": {"type": "array", "items": {"type": "string"}},
                                "compensation": {"type": "string"},
                                "location": {"type": "string"},
                                "apply_link": {"type": "string"}
                            },
                            "required": ["job_title", "sub_division_of_organization", "key_skills", "compensation", "location", "apply_link"]
                        }
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    extracted_data.append(result['data']['extract'])
                    print(f"Successfully extracted data for job: {result['data']['extract'].get('job_title', 'Unknown Title')}")
        
        # Analyze jobs against resume
        analysis_prompt = f"""
        Please analyze the resume and job listings, and return a JSON list of the top {num_jobs} roles that best fit the candidate's experience and skills. 
        Include only the job title, compensation, and apply link for each recommended role. 
        The output should be a valid JSON array of objects in the following format, with no additional text:

        [
          {{
            "job_title": "Job Title",
            "compensation": "Compensation (if available, otherwise empty string)",
            "apply_link": "Application URL"
          }},
          ...
        ]

        Based on the following resume:
        {resume}

        And the following job listings:
        {json.dumps(extracted_data, indent=2)}
        """

        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": analysis_prompt}]
        )
        
        recommended_jobs = json.loads(completion.choices[0].message.content.strip())
        return recommended_jobs

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Error parsing response: {str(e)}")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error making request: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/analyze-jobs", response_model=JobResponse)
async def analyze_jobs(request: JobRequest):
    """
    Analyze job opportunities based on the provided resume and jobs page URL.
    """
    recommended_jobs = await scrape_and_analyze_jobs(
        resume=request.resume,
        jobs_page_url=request.jobs_page_url,
        num_jobs=request.num_jobs
    )
    return JobResponse(recommended_jobs=recommended_jobs)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)