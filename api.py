from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from generation import run_konnect


app = FastAPI(
    title="KONNECT API",
    description="Technical Troubleshooting RAG API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class QueryRequest(BaseModel):
    question: str


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "konnect"
    }


# ============================================================
# QUERY
# ============================================================

@app.post("/query")
def query_konnect(request: QueryRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    result = run_konnect(question)

    return {
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"]
    }


# ============================================================
# DOCUMENT VIEW
# ============================================================

@app.get("/documents/{document_id}")
def get_document(document_id: str):

    data_dir = Path("data").resolve()

    requested_file = (data_dir / document_id).resolve()

    # Prevent path traversal
    if data_dir not in requested_file.parents:
        raise HTTPException(
            status_code=400,
            detail="Invalid document path."
        )

    if not requested_file.is_file():
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return FileResponse(
        requested_file,
        filename=requested_file.name
    )