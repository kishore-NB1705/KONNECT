from fastapi import FastAPI
from pydantic import BaseModel

from generation import run_konnect


app = FastAPI(
    title="KONNECT API",
    description="Technical Troubleshooting RAG API",
    version="1.0.0"
)


class QueryRequest(BaseModel):

    question: str


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "konnect"
    }


@app.post("/query")
def query_konnect(
    request: QueryRequest
):

    result = run_konnect(
        request.question
    )

    return {
        "question": request.question,
        "answer": result["answer"],
        "sources": result["sources"]
    }