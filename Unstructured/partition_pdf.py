from unstructured.partition.pdf import partition_pdf
from collections import Counter
from unstructured.chunking.basic import chunk_elements

elements = partition_pdf(
    filename="data/layout-parser-paper.pdf",
    strategy="hi_res",
)

print(f"Total elements: {len(elements)}")
print("-" * 80)

for i, element in enumerate(elements[:30], start=1):
    print(f"Element {i}")
    print(f"Type: {type(element).__name__}")
    print(f"Text: {str(element)[:300]}")
    print(f"Page: {element.metadata.page_number}")
    print("-" * 80)

unique_types = set()

for element in elements:
    unique_types.add(type(element).__name__)

print("\nUnique element types found:")
for element_type in sorted(unique_types):
    print(element_type)


   

type_counts = Counter(type(element).__name__ for element in elements)

print("\nElement counts by type:")
for element_type, count in sorted(type_counts.items()):
    print(f"{element_type}: {count}")


    print("\nSample elements by type:")

seen = set()

for element in elements:
    element_type = type(element).__name__

    if element_type not in seen:
        print("\n" + "=" * 80)
        print(f"TYPE: {element_type}")
        print(f"TEXT: {str(element)[:500]}")
        print(f"PAGE: {element.metadata.page_number}")

        seen.add(element_type)

chunks = chunk_elements(
    elements,
    max_characters=1000,
    new_after_n_chars=800,
)

print(f"\nTotal chunks: {len(chunks)}")
print("-" * 80)

for i, chunk in enumerate(chunks[:10], start=1):
    print(f"Chunk {i}")
    print(f"Type: {type(chunk).__name__}")
    print(f"Text: {str(chunk)[:1000]}")
    print("-" * 80)

    print("\nTABLE-RELATED CHUNKS")
print("=" * 80)

for i, chunk in enumerate(chunks, start=1):
    chunk_type = type(chunk).__name__

    if chunk_type in ["Table", "TableChunk"]:
        print(f"\nChunk {i}")
        print(f"Type: {chunk_type}")
        print(f"Text: {str(chunk)[:1500]}")
        print("-" * 80)