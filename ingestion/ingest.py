from pathlib import Path
import json

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


DATA_DIR = Path("data")


# ============================================================
# FILE TYPE DETECTION
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".txt",
    ".log",
    ".json",
}


# ============================================================
# DOMAIN DETECTION
# ============================================================

def detect_domain(file_path: Path) -> str:

    parent = file_path.parent.name.lower()

    if parent in {
        "jboss",
        "oracle",
        "application",
        "incidents",
        "error_codes",
        "troubleshooting",
    }:
        return parent

    return "unknown"


# ============================================================
# DOCUMENT TYPE DETECTION
# ============================================================

def detect_document_type(file_path: Path) -> str:

    extension = file_path.suffix.lower()
    parent = file_path.parent.name.lower()

    if extension == ".log":
        return "log"

    if extension == ".json":
        return "incident"

    if parent == "error_codes":
        return "error_reference"

    if parent == "troubleshooting":
        return "troubleshooting"

    return "technical_document"


# ============================================================
# JSON LOADER
# ============================================================

def load_json_file(file_path: Path) -> Document:

    data = json.loads(
        file_path.read_text(
            encoding="utf-8"
        )
    )

    content = json.dumps(
        data,
        indent=2
    )

    metadata = {
        "source": str(file_path),
        "file_name": file_path.name,
        "file_type": "json",
        "document_type": detect_document_type(file_path),
        "domain": detect_domain(file_path),
    }

    # Add useful incident metadata when available

    for field in [
        "incident_id",
        "error_code",
        "environment",
        "application",
        "server",
        "jboss_version",
    ]:

        if field in data:
            metadata[field] = str(
                data[field]
            )

    return Document(
        page_content=content,
        metadata=metadata
    )


# ============================================================
# TEXT / LOG LOADER
# ============================================================

def load_text_file(file_path: Path) -> Document:

    content = file_path.read_text(
        encoding="utf-8"
    )

    metadata = {
        "source": str(file_path),
        "file_name": file_path.name,
        "file_type": file_path.suffix.lower().replace(".", ""),
        "document_type": detect_document_type(file_path),
        "domain": detect_domain(file_path),
    }

    return Document(
        page_content=content,
        metadata=metadata
    )


# ============================================================
# LOAD ALL DOCUMENTS
# ============================================================

def load_documents():

    documents = []

    for file_path in DATA_DIR.rglob("*"):

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        if file_path.name == "dataset_manifest.json":
            continue

        if file_path.suffix.lower() == ".json":
            document = load_json_file(
                file_path
            )
        else:
            document = load_text_file(
                file_path
            )

        documents.append(document)

    return documents


# ============================================================
# CHUNK DOCUMENTS
# ============================================================

def chunk_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = splitter.split_documents(
        documents
    )

    for index, chunk in enumerate(chunks):

        chunk.metadata["chunk_id"] = index

    return chunks


# ============================================================
# MAIN
# ============================================================

def run_ingestion():

    print("Starting KONNECT ingestion...")

    documents = load_documents()

    print(
        f"Documents loaded: {len(documents)}"
    )

    chunks = chunk_documents(
        documents
    )

    print(
        f"Chunks created: {len(chunks)}"
    )

    if chunks:

        print("\nSample chunk:")
        print("-" * 60)

        print(
            chunks[0].page_content[:500]
        )

        print("\nMetadata:")
        print(
            chunks[0].metadata
        )

    return chunks


if __name__ == "__main__":

    run_ingestion()