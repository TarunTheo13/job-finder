import requests
import json

def analyze_jobs(resume: str, jobs_url: str = None, num_jobs: int = 3):
    """
    Call the job analysis API with the given parameters.
    
    Args:
        resume (str): The resume text to analyze
        jobs_url (str, optional): URL of the jobs page to scrape. Defaults to Google Careers.
        num_jobs (int, optional): Number of jobs to analyze. Defaults to 3.
    """
    url = "http://localhost:8000/analyze-jobs"
    
    # Prepare the request payload
    payload = {
        "resume": resume,
        "num_jobs": num_jobs
    }
    
    # Add jobs_url if provided
    if jobs_url:
        payload["jobs_page_url"] = jobs_url
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        # Make the API request
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse and print the results
        results = response.json()
        print("\nRecommended Jobs:")
        print("================")
        
        for i, job in enumerate(results["recommended_jobs"], 1):
            print(f"\n{i}. {job['job_title']}")
            print(f"   Compensation: {job['compensation']}")
            print(f"   Apply Link: {job['apply_link']}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running (python job_agent.py)")
    except requests.exceptions.HTTPError as e:
        print(f"Error: API request failed with status code {e.response.status_code}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Example resume
    example_resume = """Eric Ciarla
Co-Founder @ Firecrawl
San Francisco, California, United States

Summary
Building data extraction infrastructure for AI.

Experience
Firecrawl
Co-Founder
April 2024 - Present (6 months)
San Francisco, California, United States
Firecrawl by Mendable. Building data extraction infrastructure for AI. Used by
Amazon, Zapier, and Nvidia (YC S22)"""

    # Call the API with example data
    analyze_jobs(
        resume=example_resume,
        jobs_url="https://www.google.com/about/careers/applications/jobs/results",
        num_jobs=3
    )
