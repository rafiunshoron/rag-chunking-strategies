from langchain_text_splitters import HTMLSemanticPreservingSplitter


# Load the same HTML
with open("data/session3_html.html", "r", encoding="utf-8") as file:
    html_text = file.read()


headers_to_split_on = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
    ("h3", "Header 3"),
]


splitter = HTMLSemanticPreservingSplitter(
    headers_to_split_on=headers_to_split_on,
    max_chunk_size=50,
    elements_to_preserve=["table", "ul"],
    separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
)

chunks = splitter.split_text(html_text)


print(f"Number of chunks: {len(chunks)}")


for i, chunk in enumerate(chunks, start=1):

    print("\n" + "=" * 70)
    print(f"CHUNK {i}")
    print(f"Length: {len(chunk.page_content)} characters")
    print("=" * 70)

    print("METADATA:")
    print(chunk.metadata)

    print("\nCONTENT:")
    print(chunk.page_content)