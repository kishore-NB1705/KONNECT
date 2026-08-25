from fastapi import FastAPI, HTTPException
from generation import run_konnect

app = FastAPI(
    title="KONNECT API",
    description="Technical Troubleshooting RAG API",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "konnect"
    }


@app.post("/query")
async def query_konnect(request: dict):
    question = request.get("question")

    if not isinstance(question, str) or not question.strip():
        raise HTTPException(
            status_code=400,
            detail="question must be a non-empty string"
        )

    result = run_konnect(question.strip())

    return {
        "question": question.strip(),
        "answer": result["answer"],
        "sources": result["sources"]
    }