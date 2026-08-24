from sentence_transformers import CrossEncoder


RERANKER_MODEL = (
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def create_reranker():

    print("Loading reranker...")

    return CrossEncoder(
        RERANKER_MODEL
    )


def rerank_documents(
    reranker,
    question,
    candidates,
    top_k=5
):

    if not candidates:
        return []

    pairs = []

    for document, _ in candidates:

        pairs.append(
            (
                question,
                document.page_content
            )
        )

    scores = reranker.predict(
        pairs
    )

    ranked = sorted(
        zip(
            candidates,
            scores
        ),
        key=lambda item: item[1],
        reverse=True
    )

    results = []

    for (
        (document, retrieval_score),
        rerank_score
    ) in ranked[:top_k]:

        results.append(
            (
                document,
                float(rerank_score)
            )
        )

    return results