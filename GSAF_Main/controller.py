from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from main import run_analysis


app = FastAPI(
    title="PageRanking Studio API",
    description="SEO, AEO and GEO relevance and ranking engine",
    version="1.0.0"
)

# allows frontend to communicate with backend from a different origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


class AnalyzeRequest(BaseModel):
    url: str
    keyword: Optional[str] = ""
    keywords: Optional[List[str]] = []
    competitor_url: Optional[str] = ""


@app.get("/")
def root():
    return {"message": "PageRanking Studio API is running"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        results = run_analysis(
            url=request.url,
            keyword=request.keyword,
            keywords=request.keywords,
            competitor_url=request.competitor_url
        )
        return {
            "url": request.url,
            "keyword": request.keyword,
            "total_metrics": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))