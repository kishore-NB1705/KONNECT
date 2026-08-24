from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "konnect_knowledge"


def create_embedding_model():

    print("Loading embedding model...")

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        }
    )


def load_vector_store(embedding_model):

    print("Loading ChromaDB...")

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=CHROMA_DIR,
    )


def vector_search(
    vector_store,
    question,
    k=10
):

    results = vector_store.similarity_search_with_score(
        question,
        k=k
    )

    return results