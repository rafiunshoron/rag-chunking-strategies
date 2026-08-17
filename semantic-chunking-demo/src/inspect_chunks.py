from pathlib import Path
import json


# ============================================================
# CONFIGURATION
# ============================================================

NUMBER_TO_DISPLAY = 10

SMALL_CHUNK_THRESHOLD = 200

LARGE_CHUNK_THRESHOLD = 2000


# ============================================================
# 1. PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHUNKS_PATH = PROJECT_ROOT / "outputs" / "semantic_chunks.json"


# ============================================================
# 2. CHECK FILE EXISTS
# ============================================================

if not CHUNKS_PATH.exists():
    raise FileNotFoundError(
        f"Semantic chunks file not found:\n{CHUNKS_PATH}"
    )


# ============================================================
# 3. LOAD SAVED SEMANTIC CHUNKS
# ============================================================

with open(
    CHUNKS_PATH,
    "r",
    encoding="utf-8"
) as file:

    chunks = json.load(file)


print("=" * 80)
print("SEMANTIC CHUNK INSPECTION")
print("=" * 80)

print(f"Total chunks loaded: {len(chunks)}")


# ============================================================
# 4. SORT CHUNKS BY SIZE
# ============================================================

sorted_chunks = sorted(
    chunks,
    key=lambda chunk: chunk["characters"]
)


# ============================================================
# 5. DISPLAY SMALLEST CHUNKS
# ============================================================

print("\n" + "=" * 80)
print(f"{NUMBER_TO_DISPLAY} SMALLEST CHUNKS")
print("=" * 80)


for chunk in sorted_chunks[:NUMBER_TO_DISPLAY]:

    print("\n" + "-" * 80)

    print(f"Chunk ID   : {chunk['chunk_id']}")

    print(
        f"Characters : "
        f"{chunk['characters']}"
    )

    print(
        f"Page       : "
        f"{chunk['metadata'].get('page_label', 'Unknown')}"
    )

    print("\nTEXT:")

    print(chunk["text"])


# ============================================================
# 6. DISPLAY LARGEST CHUNKS
# ============================================================

print("\n" + "=" * 80)
print(f"{NUMBER_TO_DISPLAY} LARGEST CHUNKS")
print("=" * 80)


largest_chunks = sorted(
    chunks,
    key=lambda chunk: chunk["characters"],
    reverse=True
)


for chunk in largest_chunks[:NUMBER_TO_DISPLAY]:

    print("\n" + "-" * 80)

    print(f"Chunk ID   : {chunk['chunk_id']}")

    print(
        f"Characters : "
        f"{chunk['characters']}"
    )

    print(
        f"Page       : "
        f"{chunk['metadata'].get('page_label', 'Unknown')}"
    )

    print("\nTEXT:")

    print(chunk["text"][:2500])


# ============================================================
# 7. COUNT SMALL CHUNKS
# ============================================================

small_chunks = [
    chunk
    for chunk in chunks
    if chunk["characters"] < SMALL_CHUNK_THRESHOLD
]


# ============================================================
# 8. COUNT LARGE CHUNKS
# ============================================================

large_chunks = [
    chunk
    for chunk in chunks
    if chunk["characters"] > LARGE_CHUNK_THRESHOLD
]


# ============================================================
# 9. SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("SIZE ANALYSIS SUMMARY")
print("=" * 80)

print(
    f"Chunks smaller than "
    f"{SMALL_CHUNK_THRESHOLD} chars : "
    f"{len(small_chunks)}"
)

print(
    f"Chunks larger than "
    f"{LARGE_CHUNK_THRESHOLD} chars : "
    f"{len(large_chunks)}"
)

print(
    f"Normal-size chunks               : "
    f"{len(chunks) - len(small_chunks) - len(large_chunks)}"
)

print("\nInspection complete.")