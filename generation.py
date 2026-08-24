from langchain_ollama import ChatOllama
import os
from pathlib import Path

from retrieval import (
    create_embedding_model,
    load_vector_store,
    vector_search
)

from reranker import (
    create_reranker,
    rerank_documents
)

from ingestion.ingest import (
    load_documents,
    chunk_documents
)

from rank_bm25 import BM25Okapi


# ============================================================
# KONNECT CONFIGURATION
# ============================================================

VECTOR_TOP_K = 10
BM25_TOP_K = 10
HYBRID_TOP_K = 10
FINAL_TOP_K = 5

RRF_K = 60


# ============================================================
# LLM
# ============================================================

def create_llm():

    print("Loading LLM...")

    ollama_base_url = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )

    print(
        f"Ollama URL: {ollama_base_url}"
    )

    llm = ChatOllama(
        model="llama3.2:3b",
        temperature=0,
        base_url=ollama_base_url
    )

    return llm


# ============================================================
# DOCUMENT KEY
# ============================================================

def document_key(document):

    source = document.metadata.get(
        "source",
        ""
    )

    chunk_id = document.metadata.get(
        "chunk_id",
        ""
    )

    return f"{source}::chunk_{chunk_id}"


# ============================================================
# BUILD CONTEXT
# ============================================================

def build_context(results):

    print("Building context...")

    context_parts = []

    for index, item in enumerate(
        results,
        start=1
    ):

        # Reranker normally returns:
        # (Document, reranker_score)

        if isinstance(item, tuple):

            document = item[0]

        else:

            document = item

        source = document.metadata.get(
            "source",
            "unknown"
        )

        content = document.page_content

        context_parts.append(
            f"""
SOURCE {index}

File:
{source}

Content:
{content}
"""
        )

    return "\n".join(
        context_parts
    )


# ============================================================
# GROUNDED PROMPT
# ============================================================

def create_prompt(
    question,
    context
):

    prompt = f"""
You are KONNECT, a technical troubleshooting assistant.

Answer the user's question using ONLY the retrieved context
provided below.

Rules:

1. Do not invent information.
2. Do not use outside knowledge.
3. If the context does not contain enough evidence,
   clearly say that there is not enough information.
4. Keep the answer technically accurate.
5. Mention the relevant source number when possible.

User Question:
{question}

Retrieved Context:
{context}

Answer:
"""

    return prompt


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(
    llm,
    prompt
):

    print("Generating answer...")

    response = llm.invoke(
        prompt
    )

    return response.content


# ============================================================
# BM25 SEARCH
# ============================================================

def bm25_search(
    chunks,
    question,
    k=10
):

    print()
    print("Running BM25 search...")

    # --------------------------------------------------------
    # Tokenize documents
    # --------------------------------------------------------

    tokenized_documents = []

    for chunk in chunks:

        tokens = (
            chunk.page_content
            .lower()
            .split()
        )

        tokenized_documents.append(
            tokens
        )

    # --------------------------------------------------------
    # Create BM25
    # --------------------------------------------------------

    bm25 = BM25Okapi(
        tokenized_documents
    )

    # --------------------------------------------------------
    # Tokenize query
    # --------------------------------------------------------

    query_tokens = (
        question
        .lower()
        .split()
    )

    # --------------------------------------------------------
    # Calculate BM25 scores
    # --------------------------------------------------------

    scores = bm25.get_scores(
        query_tokens
    )

    # --------------------------------------------------------
    # Rank documents
    # --------------------------------------------------------

    ranked_indexes = sorted(
        range(len(scores)),
        key=lambda index: scores[index],
        reverse=True
    )

    # --------------------------------------------------------
    # Get top K
    # --------------------------------------------------------

    results = []

    for index in ranked_indexes[:k]:

        results.append(
            chunks[index]
        )

    print(
        f"BM25 candidates: {len(results)}"
    )

    return results


# ============================================================
# RECIPROCAL RANK FUSION
# ============================================================

def reciprocal_rank_fusion(
    vector_results,
    bm25_results,
    k=60,
    top_k=10
):

    print()
    print("Combining vector + BM25...")

    rrf_scores = {}

    documents = {}

    # ========================================================
    # VECTOR RESULTS
    # ========================================================

    for rank, item in enumerate(
        vector_results,
        start=1
    ):

        # vector_search() returns:
        # (Document, similarity_score)

        if isinstance(item, tuple):

            document = item[0]

        else:

            document = item

        key = document_key(
            document
        )

        documents[key] = document

        rrf_score = (
            1.0 /
            (k + rank)
        )

        rrf_scores[key] = (
            rrf_scores.get(
                key,
                0
            )
            + rrf_score
        )

    # ========================================================
    # BM25 RESULTS
    # ========================================================

    for rank, document in enumerate(
        bm25_results,
        start=1
    ):

        key = document_key(
            document
        )

        documents[key] = document

        rrf_score = (
            1.0 /
            (k + rank)
        )

        rrf_scores[key] = (
            rrf_scores.get(
                key,
                0
            )
            + rrf_score
        )

    # ========================================================
    # SORT BY RRF SCORE
    # ========================================================

    ranked_results = sorted(
        rrf_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # ========================================================
    # CREATE HYBRID RESULTS
    #
    # IMPORTANT:
    # reranker.py expects:
    #
    # [
    #     (Document, score),
    #     (Document, score)
    # ]
    #
    # Therefore we keep the RRF score here.
    # ========================================================

    hybrid_results = []

    for key, score in ranked_results[:top_k]:

        document = documents[key]

        hybrid_results.append(
            (
                document,
                score
            )
        )

    print(
        f"Hybrid candidates: "
        f"{len(hybrid_results)}"
    )

    return hybrid_results


# ============================================================
# MAIN KONNECT RAG PIPELINE
# ============================================================

def run_konnect(
    question
):

    print()
    print("=" * 60)
    print("Starting KONNECT end-to-end RAG...")
    print("=" * 60)

    # ========================================================
    # 1. CREATE EMBEDDING MODEL
    # ========================================================

    embedding_model = (
        create_embedding_model()
    )

    # ========================================================
    # 2. LOAD CHROMADB
    # ========================================================

    vector_store = (
        load_vector_store(
            embedding_model
        )
    )

    # ========================================================
    # 3. VECTOR SEARCH
    # ========================================================

    print()
    print("Running vector search...")

    vector_results = vector_search(
        vector_store,
        question,
        k=VECTOR_TOP_K
    )

    print(
        f"Vector candidates: "
        f"{len(vector_results)}"
    )

    # ========================================================
    # 4. LOAD DOCUMENTS FOR BM25
    # ========================================================

    print()
    print("Loading documents for BM25...")

    documents = load_documents()

    chunks = chunk_documents(
        documents
    )

    print(
        f"Documents available for BM25: "
        f"{len(chunks)}"
    )

    # ========================================================
    # 5. BM25 SEARCH
    # ========================================================

    bm25_results = bm25_search(
        chunks,
        question,
        k=BM25_TOP_K
    )

    # ========================================================
    # 6. RRF
    # ========================================================

    hybrid_results = (
        reciprocal_rank_fusion(
            vector_results,
            bm25_results,
            k=RRF_K,
            top_k=HYBRID_TOP_K
        )
    )

    # ========================================================
    # 7. LOAD RERANKER
    # ========================================================

    print()
    print("Loading reranker...")

    reranker = create_reranker()

    # ========================================================
    # 8. RERANK
    # ========================================================

    print()
    print("Reranking candidates...")

    final_results = rerank_documents(
        reranker,
        question,
        hybrid_results,
        top_k=FINAL_TOP_K
    )

    print(
        f"Final retrieved chunks: "
        f"{len(final_results)}"
    )

    # ========================================================
    # 9. BUILD CONTEXT
    # ========================================================

    context = build_context(
        final_results
    )

    # ========================================================
    # 10. BUILD GROUNDED PROMPT
    # ========================================================

    print()
    print("Building grounded prompt...")

    prompt = create_prompt(
        question,
        context
    )

    # ========================================================
    # 11. LOAD LLM
    # ========================================================

    llm = create_llm()

    # ========================================================
    # 12. GENERATE ANSWER
    # ========================================================

    answer = generate_answer(
        llm,
        prompt
    )

    # ========================================================
    # 13. COLLECT SOURCES
    # ========================================================

    sources = []

    for item in final_results:

        if isinstance(item, tuple):
            document = item[0]
        else:
            document = item

        source = document.metadata.get(
            "source",
            "unknown"
        )

        file_name = document.metadata.get(
            "file_name",
            Path(source).name
        )

        sources.append({
            "file_name": file_name,
            "source": source,
            "chunk_id": document.metadata.get(
                "chunk_id",
                ""
            )
        })

    # ========================================================
    # 14. RETURN RESULT
    # ========================================================

    return {
        "answer": answer,
        "sources": sources
    }


# ============================================================
# CLI TEST
# ============================================================

def main():

    question = (
        "What causes application connectivity failures?"
    )

    result = run_konnect(
        question
    )

    print()
    print("=" * 60)
    print("KONNECT ANSWER")
    print("=" * 60)
    print()

    print(
        result["answer"]
    )

    print()
    print("=" * 60)
    print("SOURCES")
    print("=" * 60)

    for index, source in enumerate(
        result["sources"],
        start=1
    ):

        print(
            f"{index}. {source}"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()