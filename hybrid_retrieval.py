from rank_bm25 import BM25Okapi
from langchain_core.documents import Document


def load_all_documents(vector_store):

    data = vector_store._collection.get(
        include=[
            "documents",
            "metadatas"
        ]
    )

    documents = []

    ids = data.get("ids", [])
    contents = data.get("documents", [])
    metadatas = data.get("metadatas", [])

    for index in range(len(ids)):

        documents.append(
            Document(
                page_content=contents[index],
                metadata=metadatas[index]
            )
        )

    return documents


def bm25_search(
    documents,
    question,
    k=10
):

    if not documents:
        return []

    tokenized_documents = [
        document.page_content.lower().split()
        for document in documents
    ]

    bm25 = BM25Okapi(
        tokenized_documents
    )

    query_tokens = (
        question.lower().split()
    )

    scores = bm25.get_scores(
        query_tokens
    )

    ranked_indexes = sorted(
        range(len(scores)),
        key=lambda index: scores[index],
        reverse=True
    )

    results = []

    for index in ranked_indexes[:k]:

        results.append(
            (
                documents[index],
                float(scores[index])
            )
        )

    return results


def reciprocal_rank_fusion(
    vector_results,
    bm25_results,
    k=5
):

    scores = {}
    documents = {}

    # ========================================================
    # VECTOR RESULTS
    # ========================================================

    for rank, (
        document,
        distance
    ) in enumerate(
        vector_results,
        start=1
    ):

        source = document.metadata.get(
            "source",
            ""
        )

        chunk_id = document.metadata.get(
            "chunk_id",
            ""
        )

        key = f"{source}::{chunk_id}"

        documents[key] = document

        scores[key] = (
            scores.get(key, 0)
            + 1 / (60 + rank)
        )

    # ========================================================
    # BM25 RESULTS
    # ========================================================

    for rank, (
        document,
        bm25_score
    ) in enumerate(
        bm25_results,
        start=1
    ):

        source = document.metadata.get(
            "source",
            ""
        )

        chunk_id = document.metadata.get(
            "chunk_id",
            ""
        )

        key = f"{source}::{chunk_id}"

        documents[key] = document

        scores[key] = (
            scores.get(key, 0)
            + 1 / (60 + rank)
        )

    # ========================================================
    # COMBINE RANKINGS
    # ========================================================

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    results = []

    for key, score in ranked[:k]:

        document = documents[key]

        results.append(
            (
                document,
                float(score)
            )
        )

    return results