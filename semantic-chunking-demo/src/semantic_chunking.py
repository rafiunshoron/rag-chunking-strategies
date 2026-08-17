from pathlib import Path
import json
import statistics

from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "BAAI/bge-small-en-v1.5"

BUFFER_SIZE = 1

BREAKPOINT_PERCENTILE_THRESHOLD = 95

NUMBER_OF_CHUNKS_TO_DISPLAY = 5


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_PATH = PROJECT_ROOT / "data" / "nist_ai_rmf.pdf"

OUTPUT_PATH = PROJECT_ROOT / "outputs" / "semantic_chunks.json"


# ============================================================
# 2. CHECK THAT PDF EXISTS
# ============================================================

if not PDF_PATH.exists():
    raise FileNotFoundError(
        f"PDF not found at:\n{PDF_PATH}"
    )


# ============================================================
# 3. LOAD PDF
# ============================================================

print("=" * 80)
print("LOADING PDF")
print("=" * 80)

pdf_reader = PDFReader()

documents = pdf_reader.load_data(
    file=PDF_PATH
)

print(f"Documents loaded: {len(documents)}")


# ============================================================
# 4. LOAD FREE LOCAL HUGGING FACE EMBEDDING MODEL
# ============================================================

print("\n" + "=" * 80)
print("LOADING EMBEDDING MODEL")
print("=" * 80)

print(f"Embedding model: {MODEL_NAME}")

embed_model = HuggingFaceEmbedding(
    model_name=MODEL_NAME
)

print("Embedding model loaded successfully.")


# ============================================================
# 5. CREATE SEMANTIC SPLITTER
# ============================================================

semantic_splitter = SemanticSplitterNodeParser(
    embed_model=embed_model,
    buffer_size=BUFFER_SIZE,
    breakpoint_percentile_threshold=BREAKPOINT_PERCENTILE_THRESHOLD
)


# ============================================================
# 6. PERFORM SEMANTIC CHUNKING
# ============================================================

print("\n" + "=" * 80)
print("PERFORMING SEMANTIC CHUNKING")
print("=" * 80)

nodes = semantic_splitter.get_nodes_from_documents(
    documents
)

print(f"\nNumber of semantic chunks: {len(nodes)}")


# ============================================================
# 7. DISPLAY FIRST FEW CHUNKS
# ============================================================

print("\n" + "=" * 80)
print("SAMPLE SEMANTIC CHUNKS")
print("=" * 80)

for i, node in enumerate(
    nodes[:NUMBER_OF_CHUNKS_TO_DISPLAY],
    start=1
):

    text = node.get_content()

    print("\n" + "=" * 80)
    print(f"SEMANTIC CHUNK {i}")
    print("=" * 80)

    print(f"Characters: {len(text)}")

    print(f"Metadata: {node.metadata}")

    print("\nTEXT:")

    print(text[:1500])


# ============================================================
# 8. CALCULATE CHUNK STATISTICS
# ============================================================

chunk_lengths = [
    len(node.get_content())
    for node in nodes
]


print("\n" + "=" * 80)
print("CHUNK STATISTICS")
print("=" * 80)

print(f"Number of chunks : {len(chunk_lengths)}")

print(
    f"Average chars    : "
    f"{statistics.mean(chunk_lengths):.2f}"
)

print(
    f"Median chars     : "
    f"{statistics.median(chunk_lengths):.2f}"
)

print(
    f"Minimum chars    : "
    f"{min(chunk_lengths)}"
)

print(
    f"Maximum chars    : "
    f"{max(chunk_lengths)}"
)


# ============================================================
# 9. COUNT VERY SMALL AND VERY LARGE CHUNKS
# ============================================================

small_chunks = [
    length
    for length in chunk_lengths
    if length < 200
]

large_chunks = [
    length
    for length in chunk_lengths
    if length > 2000
]


print("\n" + "-" * 80)

print(
    f"Chunks < 200 chars  : "
    f"{len(small_chunks)}"
)

print(
    f"Chunks > 2000 chars : "
    f"{len(large_chunks)}"
)

print("-" * 80)


# ============================================================
# 10. SAVE ALL SEMANTIC CHUNKS TO JSON
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

saved_chunks = []

for chunk_id, node in enumerate(nodes, start=1):

    text = node.get_content()

    saved_chunks.append(
        {
            "chunk_id": chunk_id,
            "text": text,
            "characters": len(text),
            "metadata": node.metadata
        }
    )


with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        saved_chunks,
        file,
        ensure_ascii=False,
        indent=2
    )


print("\n" + "=" * 80)
print("CHUNKS SAVED")
print("=" * 80)

print(f"Saved {len(saved_chunks)} chunks to:")

print(OUTPUT_PATH)


# ============================================================
# 11. PRINT CURRENT CONFIGURATION
# ============================================================

print("\n" + "=" * 80)
print("SEMANTIC CHUNKING CONFIGURATION")
print("=" * 80)

print(f"Embedding model      : {MODEL_NAME}")

print(f"Buffer size          : {BUFFER_SIZE}")

print(
    f"Breakpoint threshold : "
    f"{BREAKPOINT_PERCENTILE_THRESHOLD}"
)


# ============================================================
# 12. FINISHED
# ============================================================

print("\n" + "=" * 80)
print("SEMANTIC CHUNKING COMPLETE")
print("=" * 80)