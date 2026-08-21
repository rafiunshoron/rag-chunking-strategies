from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

# 1. Parse / partition the PDF
elements = partition_pdf(
    filename="data/layout-parser-paper.pdf",
    strategy="hi_res",
)

print(f"Total elements: {len(elements)}")
print("=" * 80)

# 2. Chunk the parsed elements using by_title strategy
chunks = chunk_by_title(
    elements,
    max_characters=1000,
    new_after_n_chars=800,
)

print(f"\nTotal chunks: {len(chunks)}")
print("=" * 80)

# 3. Print the first 15 chunks
for i, chunk in enumerate(chunks[:15], start=1):
    print(f"\nChunk {i}")
    print(f"Type: {type(chunk).__name__}")
    print(f"Text:\n{str(chunk)}")
    print("-" * 80)