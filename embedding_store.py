from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from ingestion.ingest import load_documents, chunk_documents


# ============================================================
# KONNECT EMBEDDING + INCREMENTAL VECTOR STORE
# ============================================================

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "konnect_knowledge"


# ============================================================
# EMBEDDING MODEL
# ============================================================

def create_embedding_model():

    print("Loading embedding model...")

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        }
    )

    return embedding_model


# ============================================================
# CREATE / LOAD CHROMA
# ============================================================

def create_vector_store(embedding_model):

    print("Loading ChromaDB...")

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=CHROMA_DIR,
    )

    return vector_store


# ============================================================
# CREATE STABLE CHUNK ID
# ============================================================

def create_chunk_id(chunk):

    source = chunk.metadata["source"]
    chunk_id = chunk.metadata["chunk_id"]

    return f"{source}::chunk_{chunk_id}"


# ============================================================
# INCREMENTAL INGESTION
# ============================================================

def add_new_chunks(
    vector_store,
    chunks
):

    new_chunks = []
    new_ids = []

    existing_ids = set()

    # --------------------------------------------------------
    # GET EXISTING IDS FROM CHROMA
    # --------------------------------------------------------

    existing_data = vector_store._collection.get(
        include=[]
    )

    if existing_data.get("ids"):

        existing_ids = set(
            existing_data["ids"]
        )

    print(
        f"Existing records in ChromaDB: {len(existing_ids)}"
    )

    # --------------------------------------------------------
    # CHECK EACH CHUNK
    # --------------------------------------------------------

    for chunk in chunks:

        chunk_id = create_chunk_id(
            chunk
        )

        # Already exists
        if chunk_id in existing_ids:

            continue

        # New chunk
        new_chunks.append(chunk)
        new_ids.append(chunk_id)

    # --------------------------------------------------------
    # NOTHING NEW
    # --------------------------------------------------------

    if not new_chunks:

        print(
            "No new chunks found."
        )

        return 0

    # --------------------------------------------------------
    # ADD ONLY NEW CHUNKS
    # --------------------------------------------------------

    print(
        f"New chunks to embed: {len(new_chunks)}"
    )

    vector_store.add_documents(
        documents=new_chunks,
        ids=new_ids
    )

    print(
        f"New chunks stored: {len(new_chunks)}"
    )

    return len(new_chunks)


# ============================================================
# VERIFY DATABASE
# ============================================================

def verify_vector_store(
    vector_store
):

    collection = vector_store._collection

    count = collection.count()

    print()
    print(
        f"Total vectors in ChromaDB: {count}"
    )

    # --------------------------------------------------------
    # SAMPLE RECORD
    # --------------------------------------------------------

    sample = collection.get(
        limit=1,
        include=[
            "documents",
            "metadatas",
            "embeddings"
        ]
    )

    if not sample["documents"]:

        return

    print()
    print("Sample stored document:")
    print("-" * 60)

    print(
        sample["documents"][0][:300]
    )

    print()
    print("Sample metadata:")

    print(
        sample["metadatas"][0]
    )

    print()
    print("Embedding vector dimension:")

    print(
        len(sample["embeddings"][0])
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    print(
        "Starting KONNECT incremental ingestion..."
    )

    print()

    # --------------------------------------------------------
    # 1. LOAD DOCUMENTS
    # --------------------------------------------------------

    documents = load_documents()

    print(
        f"Documents loaded: {len(documents)}"
    )

    # --------------------------------------------------------
    # 2. CHUNK DOCUMENTS
    # --------------------------------------------------------

    chunks = chunk_documents(
        documents
    )

    print(
        f"Chunks created: {len(chunks)}"
    )

    # --------------------------------------------------------
    # 3. LOAD EMBEDDING MODEL
    # --------------------------------------------------------

    embedding_model = create_embedding_model()

    # --------------------------------------------------------
    # 4. LOAD EXISTING CHROMA
    # --------------------------------------------------------

    vector_store = create_vector_store(
        embedding_model
    )

    # --------------------------------------------------------
    # 5. ADD ONLY NEW CHUNKS
    # --------------------------------------------------------

    add_new_chunks(
        vector_store,
        chunks
    )

    # --------------------------------------------------------
    # 6. VERIFY
    # --------------------------------------------------------

    verify_vector_store(
        vector_store
    )

    print()
    print(
        "KONNECT incremental ingestion completed."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()