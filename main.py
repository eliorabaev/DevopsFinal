from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import string
import random
import time
from typing import Dict, Optional

# Initialize FastAPI app
app = FastAPI(title="URL Shortener Service", version="1.0.0")

# In-memory storage (use database in production)
url_database: Dict[str, str] = {}

# Prometheus metrics
urls_created_counter = Counter("urls_created_total", "Total number of URLs created")
redirects_counter = Counter("redirects_total", "Total number of redirects performed")
request_duration = Histogram(
    "request_duration_seconds", "Request duration in seconds", ["method", "endpoint"]
)


# Pydantic models
class URLRequest(BaseModel):
    url: HttpUrl
    custom_code: Optional[str] = None


class URLResponse(BaseModel):
    short_url: str
    original_url: str
    short_code: str


# Helper function to generate random short code
def generate_short_code(length: int = 6) -> str:
    """Generate a random short code using letters and digits"""
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


# Helper function to check if code exists
def code_exists(code: str) -> bool:
    """Check if a short code already exists in database"""
    return code in url_database


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "URL Shortener Service",
        "version": "1.0.0",
        "endpoints": {
            "shorten": "POST /shorten - Create a short URL",
            "redirect": "GET /{short_code} - Redirect to original URL",
            "metrics": "GET /metrics - Prometheus metrics",
        },
    }


@app.post("/shorten", response_model=URLResponse)
async def shorten_url(request: URLRequest, req: Request):
    """Create a shortened URL"""
    start_time = time.time()

    try:
        original_url = str(request.url)

        # Use custom code if provided, otherwise generate random one
        if request.custom_code:
            if code_exists(request.custom_code):
                raise HTTPException(
                    status_code=400, detail="Custom code already exists"
                )
            short_code = request.custom_code
        else:
            # Generate unique short code
            short_code = generate_short_code()
            while code_exists(short_code):
                short_code = generate_short_code()

        # Store in database
        url_database[short_code] = original_url

        # Update metrics
        urls_created_counter.inc()

        # Create response
        base_url = str(req.base_url).rstrip("/")
        short_url = f"{base_url}/{short_code}"

        return URLResponse(
            short_url=short_url, original_url=original_url, short_code=short_code
        )

    finally:
        # Record request duration
        duration = time.time() - start_time
        request_duration.labels(method="POST", endpoint="/shorten").observe(duration)


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/stats")
async def get_stats():
    """Get basic statistics about the service"""
    return {
        "total_urls": len(url_database),
        "total_redirects": redirects_counter._value._value,
        "total_urls_created": urls_created_counter._value._value,
    }


# Commented endpoint for live demo (DO NOT UNCOMMENT YET)
# @app.get("/cicd-test")
# async def cicd_test():
#     return {"message": "CI/CD Pipeline Working!", "status": "success"}


@app.get("/{short_code}")
async def redirect_url(short_code: str):
    """Redirect to the original URL using short code"""
    start_time = time.time()

    try:
        if short_code == "metrics":
            # Handle metrics endpoint to avoid conflict
            return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

        if short_code not in url_database:
            raise HTTPException(status_code=404, detail="Short code not found")

        original_url = url_database[short_code]

        # Update metrics
        redirects_counter.inc()

        return RedirectResponse(url=original_url, status_code=301)

    finally:
        # Record request duration
        duration = time.time() - start_time
        request_duration.labels(method="GET", endpoint="/{short_code}").observe(
            duration
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
