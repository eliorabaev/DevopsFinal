from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import string
import random
import time
from typing import Dict, Optional

app = FastAPI(title="URL Shortener Service", version="1.0.0")

url_database: Dict[str, str] = {}

urls_created_counter = Counter("urls_created_total", "Total number of URLs created")
redirects_counter = Counter("redirects_total", "Total number of redirects performed")
request_duration = Histogram(
    "request_duration_seconds", "Request duration in seconds", ["method", "endpoint"]
)


class URLRequest(BaseModel):
    url: HttpUrl
    custom_code: Optional[str] = None


class URLResponse(BaseModel):
    short_url: str
    original_url: str
    short_code: str


def generate_short_code(length: int = 6) -> str:
    """Generate a random short code using letters and digits"""
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


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

        if request.custom_code:
            if code_exists(request.custom_code):
                raise HTTPException(
                    status_code=400, detail="Custom code already exists"
                )
            short_code = request.custom_code
        else:
            short_code = generate_short_code()
            while code_exists(short_code):
                short_code = generate_short_code()

        url_database[short_code] = original_url

        urls_created_counter.inc()

        base_url = str(req.base_url).rstrip("/")
        short_url = f"{base_url}/{short_code}"

        return URLResponse(
            short_url=short_url, original_url=original_url, short_code=short_code
        )

    finally:
        duration = time.time() - start_time
        request_duration.labels(method="POST", endpoint="/shorten").observe(duration)


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/stats")
async def get_stats():
    """Get basic statistics about the service"""

    current_urls_created = urls_created_counter._value.get()
    current_redirects = redirects_counter._value.get()

    return {
        "total_urls": len(url_database),
        "total_redirects": current_redirects,
        "total_urls": current_urls_created,
        "info": "Counter values reset on service restart - this is normal Prometheus behavior. Use increase() function in Grafana for historical totals.",
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
            return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

        if short_code not in url_database:
            raise HTTPException(status_code=404, detail="Short code not found")

        original_url = url_database[short_code]

        redirects_counter.inc()

        return RedirectResponse(url=original_url, status_code=301)

    finally:
        duration = time.time() - start_time
        request_duration.labels(method="GET", endpoint="/{short_code}").observe(
            duration
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
