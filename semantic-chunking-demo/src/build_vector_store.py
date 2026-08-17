from pathlib import Path
import json

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "BAAI/bge-small-en-v1.5"

COLLECTION_NAME = "semantic_chunks"


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHUNKS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "semantic_chunks.json"
)

CHROMA_PATH = (
    PROJECT_ROOT
    / "chroma_db"
)


# ============================================================
# 2. CHECK THAT CHUNKS FILE EXISTS
# ============================================================

if not CHUNKS_PATH.exists():

    raise FileNotFoundError(
        f"Semantic chunks file not found:\n{CHUNKS_PATH}"
    )


# ============================================================
# 3. LOAD SAVED SEMANTIC CHUNKS
# ============================================================

print("=" * 80)
print("LOADING SAVED SEMANTIC CHUNKS")
print("=" * 80)


with open(
    CHUNKS_PATH,
    "r",
    encoding="utf-8"
) as file:

    saved_chunks = json.load(file)


print(
    f"Semantic chunks loaded: "
    f"{len(saved_chunks)}"
)


# ============================================================
# 4. CONVERT TO LANGCHAIN DOCUMENTS
# ============================================================

documents = []


for chunk in saved_chunks:

    metadata = chunk["metadata"].copy()

    metadata["chunk_id"] = chunk["chunk_id"]

    metadata["characters"] = chunk["characters"]

    metadata["chunking_strategy"] = "semantic"


    document = Document(

        page_content=chunk["text"],

        metadata=metadata
    )


    documents.append(document)


print(
    f"LangChain Documents created: "
    f"{len(documents)}"
)


# ============================================================
# 5. LOAD FREE LOCAL HUGGING FACE EMBEDDING MODEL
# ============================================================

print("\n" + "=" * 80)
print("LOADING EMBEDDING MODEL")
print("=" * 80)

print(
    f"Embedding model: "
    f"{MODEL_NAME}"
)


embedding_model = HuggingFaceEmbeddings(

    model_name=MODEL_NAME,

    model_kwargs={
        "device": "cpu"
    },

    encode_kwargs={
        "normalize_embeddings": True
    }
)


print(
    "Embedding model loaded successfully."
)


# ============================================================
# 6. CREATE PERSISTENT CHROMA VECTOR STORE
# ============================================================

print("\n" + "=" * 80)
print("CREATING CHROMA VECTOR STORE")
print("=" * 80)


vector_store = Chroma(

    collection_name=COLLECTION_NAME,

    embedding_function=embedding_model,

    persist_directory=str(CHROMA_PATH)
)


# ============================================================
# 7. ADD DOCUMENTS TO CHROMA
# ============================================================

ids = [
    f"semantic_chunk_{chunk['chunk_id']}"
    for chunk in saved_chunks
]


vector_store.add_documents(

    documents=documents,

    ids=ids
)


print(
    f"Documents added to Chroma: "
    f"{len(documents)}"
)


# ============================================================
# 8. TEST RETRIEVAL
# ============================================================

print("\n" + "=" * 80)
print("TEST RETRIEVAL")
print("=" * 80)


test_query = (
    "What are the main functions "
    "of the NIST AI Risk Management Framework?"
)


print(
    f"\nQuery:\n{test_query}"
)


results = vector_store.similarity_search(
    test_query,
    k=3
)


# ============================================================
# 9. DISPLAY TOP-3 RESULTS
# ============================================================

for rank, document in enumerate(
    results,
    start=1
):

    print(
        "\n" + "=" * 80
    )

    print(
        f"RESULT {rank}"
    )

    print(
        "=" * 80
    )

    print(
        f"Chunk ID: "
        f"{document.metadata.get('chunk_id')}"
    )

    print(
        f"Page: "
        f"{document.metadata.get('page_label')}"
    )

    print(
        f"Characters: "
        f"{document.metadata.get('characters')}"
    )

    print(
        "\nTEXT:"
    )

    print(
        document.page_content[:1500]
    )


# ============================================================
# 10. FINISHED
# ============================================================

print("\n" + "=" * 80)

print(
    "CHROMA VECTOR STORE CREATED SUCCESSFULLY"
)

print("=" * 80)

print(
    f"Persistent database location:\n"
    f"{CHROMA_PATH}"
)